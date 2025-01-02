let total;
let current_page = 1;
const per_page = 10;
const table = document.getElementById('body-tabela-estoque')

const handleClick = (event, {title_id, input_id, prefix}) => {
    const id = event.target.dataset.id;
    const desc = event.target.dataset.desc;

    document.getElementById(title_id).textContent = `${prefix} ${desc}`;
    document.getElementById(input_id).value = id;
};

const attach_event_listeners = (class_name, handler, handler_args) => {
    const delete_buttons = document.getElementsByClassName(class_name);

    Array.from(delete_buttons).forEach(btn => {
        btn.removeEventListener('click', handler);
        btn.addEventListener('click', (event) => handler(event, handler_args));
    });
};

const load_products = async (page) => {
    try {
        const response = await fetch(`/api/products?page=${current_page}&per_page=${per_page}`);
        const data = await response.json();
        total = data.total;

        table.innerHTML = '';

        data.products.forEach(product => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td scope="col">${product.id}</td>
                <td scope="col">${product.desc}</td>
                <td scope="col">${product.category}</td>
                <td scope="col">${product.quantity}</td>
                <td scope="col">${product.price}</td> 
                <td scope="col">
                    <button id="adicionar-${product.id}" data-bs-toggle="modal" data-bs-target="" type="button">A</button>
                    <button id="editar-${product.id}" data-bs-toggle="modal" data-bs-target="" type="button">E</button>
                    <button class="botao-deletar-produto btn btn-danger" data-id="${product.id}" data-desc="${product.desc}" data-bs-toggle="modal" data-bs-target="#modal-deleta-produto" type="button">R</button>
                </td>
            `;

            table.appendChild(row);
        });

        attach_event_listeners('botao-deletar-produto', handleClick, {
            title_id : 'titulo-modal-deleta-produto',
            input_id : 'id-produto-delete',
            prefix : 'Deletar'
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
        
        table.innerHTML = ''; // Limpar a tabela antes de cada pesquisa

        if (!data.products || data.products.length === 0) {
            table.innerHTML = '<tr><td colspan="6">Nenhum produto encontrado.</td></tr>';
            return;
        }

        data.products.forEach(product => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td scope="col">${product.id}</td>
                <td scope="col">${product.desc}</td>
                <td scope="col">${product.category}</td>
                <td scope="col">${product.quantity}</td>
                <td scope="col">${product.price}</td> 
                <td scope="col">
                    <button id="adicionar-${product.id}" data-bs-toggle="modal" data-bs-target="" type="button">A</button>
                    <button id="editar-${product.id}" data-bs-toggle="modal" data-bs-target="" type="button">E</button>
                    <button class="botao-deletar-produto btn btn-danger" data-id="${product.id}" data-desc="${product.desc}" data-bs-toggle="modal" data-bs-target="#modal-deleta-produto" type="button">R</button>
                </td>
            `;

            table.appendChild(row);
        });

        attach_event_listeners('botao-deletar-produto', handleClick, {
            title_id : 'titulo-modal-deleta-produto',
            input_id : 'id-produto-delete',
            prefix : 'Deletar'
        });
    }
    catch (error) {
        console.error('Erro na pesquisa de produtos: ', error)
    };
};

/* Modal Deleta Categorias */
document.getElementById('botao-deletar-categoria').addEventListener('click', () => {
    const id = document.getElementById('select-categoria-delete').value;
    const desc = document.getElementById('select-categoria-delete').textContent;
    document.getElementById('titulo-modal-deleta-categoria').textContent = `Deletar ${desc}`;
    document.getElementById('id-categoria-delete').value = id;
});

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

/* Carregamento dos Produtos na Tabela*/ 
document.addEventListener('DOMContentLoaded', () => load_products(current_page))