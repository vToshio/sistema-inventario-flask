let total;
let current_page = 1;
const per_page = 10;
const table = document.getElementById('body-tabela-clientes');

const disable_button = async (button_id) => {
    document.getElementById(button_id).classList.add('disabled');
}

const handleClickDisable = (event, {title_id, input_id, prefix}) => {
    const id = event.target.dataset.id;
    const name = event.target.dataset.name;

    document.getElementById(input_id).value = id;
    document.getElementById(title_id).textContent = `${prefix} ${name}`;
};

const handleClickEdit = async (event, {title_id, title_msg}) => {
    const id = event.target.dataset.id;
    const request = await fetch(`/api/customers/${id}`);
    const customer = await request.json();

    document.getElementById(title_id).textContent = `${title_msg} ${id}`;
    document.getElementById('id-editar-cliente').value = id;
    document.getElementById('cpf-editar-cliente').value = customer.cpf;
    document.getElementById('nome-editar-cliente').value = customer.name;
    document.getElementById('email-editar-cliente').value = customer.email;
    document.getElementById('endereco-editar-cliente').value = customer.address;
};

const attach_event_listeners = async (class_name, handler, handler_args) => {
    const buttons = document.getElementsByClassName(class_name);

    Array.from(buttons).forEach(btn => {
        btn.removeEventListener('click', handler);
        btn.addEventListener('click', (event) => handler(event, handler_args))
    });
};

const load_clients = async () => {
    try {
        const response = await fetch(`/api/customers?page${current_page}&per_page=${per_page}`);
        const data = await response.json();
        const customers = Array.from(data.customers);

        table.innerHTML = '';

        if (customers.length === 0) {
            table.innerHTML = '<tr><td colspan="6">Nenhum cliente cadastrado ou ativo no sistema.</td></tr>';
            return;
        }

        customers.forEach(customer => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td scope="col">${customer.id}</td>
                <td scope="col">${customer.name}</td>
                <td scope="col">${customer.cpf}</td>
                <td scope="col">${customer.email}</td>
                <td scope="col">${customer.address}</td>
                <td scope="col">
                    <button id="botao-editar-cliente-${customer.id}" class="botao-editar-cliente btn btn-secondary" data-id="${customer.id}" data-bs-toggle="modal" data-bs-target="#modal-editar-cliente">E</button>
                    <button id="botao-desativar-status-${customer.id}" class="botao-desativar-status btn btn-danger" data-id="${customer.id}" data-name="${customer.name}" data-bs-toggle="modal" data-bs-target="#modal-desativar-status">D</button>
                </td>
            `;
            table.appendChild(row);
        });

        attach_event_listeners('botao-editar-cliente', handleClickEdit, {
            'title_id' : 'titulo-modal-editar-cliente',
            'title_msg' : 'Editar Cliente'
        });
        attach_event_listeners('botao-desativar-status', handleClickDisable, {
            'title_id' : 'titulo-modal-desativar-status',
            'input_id' : 'id-desativar-status',
            'prefix' : 'Desativar'
        });
    } catch (e) {
        console.error(`Erro no carregamento de clientes - ${e}`);
    };
};

const search_clients = async () => {
    try {
        const query = document.getElementById('barra-pesquisa').value.trim();
        const response = await fetch(`/api/customers/search?query=${query}`);
        const data = await response.json();
        const customers = Array.from(data.customers);

        table.innerHTML = '';

        if (customers.length === 0) {
            table.innerHTML = '<tr><td colspan="5">Nenhum cliente encontrado.</td></tr>';
            return;
        }
        
        customers.forEach(customer => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td scope="col">${customer.id}</td>
                <td scope="col">${customer.name}</td>
                <td scope="col">${customer.cpf}</td>
                <td scope="col">${customer.email}</td>
                <td scope="col">${customer.address}</td>
                <td scope="col">
                    <button id="botao-editar-cliente-${customer.id}" class="botao-editar-cliente btn btn-secondary" data-id="${customer.id}" data-bs-toggle="modal" data-bs-target="#modal-editar-cliente">E</button>
                    <button id="botao-desativar-status-${customer.id}" class="botao-desativar-status btn btn-danger" data-id="${customer.id}" data-name="${customer.name}" data-bs-toggle="modal" data-bs-target="#modal-desativar-status">D</button>
                </td>
            `;
            table.appendChild(row);

            if (!customer.status) {
                disable_button(`botao-editar-cliente-${customer.id}`);
                disable_button(`botao-desativar-status-${customer.id}`)
            }
        });

        attach_event_listeners('botao-editar-cliente', handleClickEdit, {
            'title_id' : 'titulo-modal-editar-cliente',
            'title_msg' : 'Editar Cliente'
        });
        attach_event_listeners('botao-desativar-status', handleClickDisable, {
            'title_id' : 'titulo-modal-desativar-status',
            'input_id' : 'id-desativar-status',
            'prefix' : 'Desativar'
        });
    } catch (e) {
        console.error(`Erro na pesquisa - ${e}`);
    };
};

document.getElementById('botao-pesquisa').addEventListener('click', () => search_clients());

/* Botões de Paginação*/
document.getElementById('anterior').addEventListener('click', () => {
    if (current_page>1) 
        load_products(current_page-1);
});
document.getElementById('proxima').addEventListener('click', () => {
    if (current_page<total)
        load_products(current_page+1);
});

document.addEventListener('DOMContentLoaded', () => {
    load_clients();
});