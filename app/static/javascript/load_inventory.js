const table = document.getElementById('body-tabela-estoque');
const user_role = document.getElementById('user_role').value; 
let current_page = 1;
const per_page = 10;
let total;

const enable_buttons = async (class_name) => {
    await Array.from(document.getElementsByClassName(class_name)).forEach(btn => {
        btn.classList.remove('disabled');
    });
};

const disable_buttons = async (class_name) => {
    await Array.from(document.getElementsByClassName(class_name)).forEach(btn => {
        btn.classList.add('disabled');
    });
};

const disable_button = async (button_id) => {
    document.getElementById(button_id).classList.add('disabled');
}

const enable_button = async (button_id) => {
    document.getElementById(button_id).classList.remove('disabled');
}


const populate_select = async () => {
    try {
        const response = await fetch('/api/categories');
        const data = await response.json();
        let categories = data.categories;

        const select = document.getElementById('select-categoria-editar');
        select.innerHTML = '';
        
        categories.forEach(category => {   
            const option = document.createElement('option');
            option.value = category.id;
            option.textContent = category.desc ;
            select.appendChild(option); 
        });
    } catch (e) {
        console.error('Erro ao carregar categorias - ', e);
    };
};

const handleClick = (event, {title_id, input_id, prefix}) => {
    const id = event.target.dataset.id;
    const desc = event.target.dataset.desc;

    document.getElementById(title_id).textContent = `${prefix} ${desc}`;
    document.getElementById(input_id).value = id;
};

const handleClickEdit = async (event, {prefix}) => {
    const id = event.target.dataset.id;
    const desc = event.target.dataset.desc;
    const price = event.target.dataset.price;
    const category_id = event.target.dataset.categoryid;

    document.getElementById('titulo-modal-editar-produto').textContent = `${prefix}`;
    document.getElementById('id-produto-editar').value = id;
    document.getElementById('desc-produto-editar').value = desc;
    document.getElementById('preco-produto-editar').value = price;

    await populate_select();
    document.getElementById('select-categoria-editar').value = category_id;
};

const attach_event_listeners = (class_name, handler, handler_args) => {
    const buttons = document.getElementsByClassName(class_name);

    Array.from(buttons).forEach(btn => {
        btn.removeEventListener('click', handler);
        btn.addEventListener('click', (event) => handler(event, handler_args));
    });
};

const load_products = async (page) => {
    try {
        const response = await fetch(`/api/products?page=${current_page}&per_page=${per_page}`);
        const data = await response.json();
        const products = Array.from(data.products);

        table.innerHTML = '';

        if (products.length === 0) {
            table.innerHTML = '<tr><td colspan="6">Nenhum produto cadastrado ou ativo no sistema.</td></tr>';
            return;
        }

        products.forEach(product => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td scope="col">${product.id}</td>
                <td scope="col">${product.desc}</td>
                <td scope="col">${product.category}</td>
                <td scope="col">${product.quantity}</td>
                <td scope="col">${product.price}</td> 
                <td scope="col">
                    <button class="botao-adicionar-unidades btn btn-primary" data-id="${product.id}" data-desc="${product.desc}" data-bs-toggle="modal" data-bs-target="#modal-adicionar-unidades" type="button">A</button>
                    <button class="botao-editar-produto btn btn-secondary" data-id="${product.id}" data-desc="${product.desc}" data-price='${product.price}' data-categoryid=${product.category_id} data-bs-toggle="modal" data-bs-target="#modal-editar-produto" type="button">E</button>
                    <button class="botao-desativar-produto btn btn-danger" data-id="${product.id}" data-desc="${product.desc}" data-bs-toggle="modal" data-bs-target="#modal-desativar-produto" type="button">R</button>
                </td>
            `;

            table.appendChild(row);
        });

        attach_event_listeners('botao-adicionar-unidades', handleClick, {
            title_id : 'titulo-modal-adicionar-unidades',
            input_id : 'id-produto-adicionar',
            prefix : 'Adicionar'
        });
        attach_event_listeners('botao-editar-produto', handleClickEdit, { 
            prefix : 'Editar Produto'
        });
        attach_event_listeners('botao-desativar-produto', handleClick, {
            title_id : 'titulo-modal-desativar-produto',
            input_id : 'id-desativar-produto',
            prefix : 'Desativar'
        });
        current_page = data.page;
    } 
    catch (error) {
        console.error('Erro no carregamento dos produtos: ', error);
    };
};

const search_products = async () => {
    try {
        const query = document.getElementById('barra-pesquisa').value.trim()
        const response = await fetch(`/api/products/search?query=${query}`);
        const data = await response.json();
        const products = Array.from(data.products);

        table.innerHTML = ''; 

        if (products.length === 0) {
            table.innerHTML = '<tr><td colspan="6">Nenhum produto encontrado.</td></tr>';
            return;
        }

        await products.forEach(product => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td scope="col">${product.id}</td>
                <td scope="col">${product.desc}</td>
                <td scope="col">${product.category}</td>
                <td scope="col">${product.quantity}</td>
                <td scope="col">${product.price}</td> 
                <td scope="col">
                    <button id="botao-adicionar-unidades-${product.id}" class="botao-adicionar-unidades btn btn-primary" data-id="${product.id}" data-desc="${product.desc}" data-bs-toggle="modal" data-bs-target="#modal-adicionar-unidades" type="button">A</button>
                    <button id="botao-editar-produto-${product.id}" class="botao-editar-produto btn btn-secondary" data-id="${product.id}" data-desc="${product.desc}" data-price='${product.price}' data-categoryid=${product.category_id} data-bs-toggle="modal" data-bs-target="#modal-editar-produto" type="button">E</button>
                    <button id="botao-desativar-produto-${product.id}"  class="botao-desativar-produto btn btn-danger" data-id="${product.id}" data-desc="${product.desc}" data-bs-toggle="modal" data-bs-target="#modal-desativar-produto" type="button">R</button>
                </td>
            `;
            table.appendChild(row);

            if (!product.status) {
                disable_button(`botao-adicionar-unidades-${product.id}`);
                disable_button(`botao-editar-produto-${product.id}`);
                disable_button(`botao-desativar-produto-${product.id}`);
            }
        });
        
        attach_event_listeners('botao-adicionar-unidades', handleClick, {
            title_id : 'titulo-modal-adicionar-unidades',
            input_id : 'id-produto-adicionar',
            prefix : 'Adicionar'
        });
        attach_event_listeners('botao-editar-produto', handleClickEdit, {
            title_id : 'titulo-modal-editar-produto',
            input_id : 'id-produto-editar-produto',
            prefix : 'Editar'
        });
        attach_event_listeners('botao-desativar-produto', handleClick, {
            title_id : 'titulo-modal-desativar-produto',
            input_id : 'id-desativar-produto',
            prefix : 'Desativar'
        });

        if (user_role === 'user') {
            disable_buttons('botao-editar-produto');
            disable_buttons('botao-desativar-produto');
        }
    }
    catch (error) {
        console.error('Erro na pesquisa de produtos: ', error)
    };
};

/* Modal Deleta Categorias */

try {
    document.getElementById('botao-deletar-categoria').addEventListener('click', () => {
        const id = document.getElementById('select-deletar-categoria').value;
        const desc = document.getElementById('select-deletar-categoria').textContent;
        document.getElementById('titulo-modal-deletar-categoria').textContent = `Deletar ${desc}`;
        document.getElementById('id-categoria-deletar').value = id;
    });
} catch {
    console.error('Botão de deletar categoria não encontrado');
}

/* Carregamento dos Produtos na Tabela*/ 
document.addEventListener('DOMContentLoaded', async () => {
    await load_products(current_page);

    if (user_role === 'user') {
        disable_buttons('botao-editar-produto');
        disable_buttons('botao-desativar-produto');
    } else {
        enable_buttons('botao-editar-produto');
        enable_buttons('botao-desativar-produto');
    }
   
    /* Barra de Pesquisa */
    document.getElementById('botao-pesquisa').addEventListener('click', () => search_products())
    
    /* Botões de Paginação*/
    document.getElementById('anterior').addEventListener('click', () => {
        if (current_page>1) 
            load_products(current_page-1);
    })
    document.getElementById('proxima').addEventListener('click', () => {
        if (current_page<total)
            load_products(current_page+1);
    })
});