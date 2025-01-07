let total;
let current_page = 1;
const per_page = 10;
const table = document.getElementById('body-tabela-clientes');

const handleClickDelete = (event, {title_id, input_id, prefix}) => {
    const id = event.target.dataset.id;
    const name = event.target.dataset.name;

    document.getElementById(title_id).textContent = `${prefix} ${name}`
    document.getElementById(input_id).value = id;
};

const handleClickEdit = async (event, {title_id, title_msg}) => {
    const id = event.target.dataset.id;
    const request = await fetch(`/api/customers/${id}`);
    const customer = await request.json();

    document.getElementById(title_id).textContent = `${title_msg} ${id}`;
    document.getElementById('id-editar-cliente').value = id;
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

        if (data.total === 0) {
            table.innerHTML = '<tr><td colspan="6">Nenhum cliente cadastrado no sistema.</td></tr>';
            return;
        }

        customers.forEach(client => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td scope="col">${client.id}</td>
                <td scope="col">${client.name}</td>
                <td scope="col">${client.email}</td>
                <td scope="col">${client.address}</td>
                <td scope="col">
                    <button class="botao-editar-cliente btn btn-secondary" data-id="${client.id}" data-bs-toggle="modal" data-bs-target="#modal-editar-cliente">E</button>
                    <button class="botao-deletar-cliente btn btn-danger" data-id="${client.id}" data-name="${client.name}" data-bs-toggle="modal" data-bs-target="#modal-deletar-cliente">D</button>
                </td>
            `;
            table.appendChild(row);
        });

        attach_event_listeners('botao-editar-cliente', handleClickEdit, {
            'title_id' : 'titulo-modal-editar-cliente',
            'title_msg' : 'Editar Cliente'
        });
        attach_event_listeners('botao-deletar-cliente', handleClickDelete, {
            'title_id' : 'titulo-modal-deletar-cliente',
            'input_id' : 'id-deletar-cliente',
            'prefix' : 'Deletar'
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
        
        customers.forEach(client => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td scope="col">${client.id}</td>
                <td scope="col">${client.name}</td>
                <td scope="col">${client.email}</td>
                <td scope="col">${client.address}</td>
                <td scope="col">
                    <button class="botao-editar-cliente btn btn-secondary" data-id="${client.id}">E</button>
                    <button class="botao-deletar-cliente btn btn-danger" data-id="${client.id}">D</button>
                </td>
            `;console.log(customers)
            table.appendChild(row);
        });

        attach_event_listeners('botao-editar-cliente', handleClickEdit, {
            'title_id' : 'titulo-modal-editar-cliente',
            'title_msg' : 'Editar Cliente'
        });
        attach_event_listeners('botao-deletar-cliente', handleClick, {
            'title_id' : 'titulo-modal-deletar-cliente',
            'input_id' : 'id-deletar-cliente',
            'prefix' : 'Deletar'
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
})
document.getElementById('proxima').addEventListener('click', () => {
    if (current_page<total)
        load_products(current_page+1);
})


document.addEventListener('DOMContentLoaded', () => load_clients());