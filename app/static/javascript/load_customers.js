let total;
let customers_on_screen;
let current_page = 1;
const per_page = 10;
const user_role = document.getElementById('user_role').value;
const table = document.getElementById('body-tabela-clientes');

/* HELPERS */
const disable_button = async (button_id) => {
    document.getElementById(button_id).classList.add('disabled');
}

const handleClickDisable = (event, {title_id, input_id, prefix}) => {
    const id = event.currentTarget.dataset.id;
    const name = event.currentTarget.dataset.name;

    document.getElementById(input_id).value = id;
    document.getElementById(title_id).textContent = `${prefix} ${name}`;
};

const handleClickEdit = async (event, {title_id, title_msg}) => {
    const id = event.currentTarget.dataset.id;
    const request = await fetch(`/api/customers/${id}`);
    const customer = await request.json();

    document.getElementById(title_id).textContent = `${title_msg} ${customer.id}`;
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

const render_customers = (customers) => {
    table.innerHTML = '';

    customers.forEach(customer => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td scope="col">${customer.id}</td>
            <td scope="col">${customer.name}</td>
            <td scope="col">${customer.cpf}</td>
            <td scope="col">${customer.email}</td>
            <td scope="col">${customer.address}</td>
            <td scope="col">
                <button id="botao-editar-cliente-${customer.id}" class="botao-editar-cliente btn btn-secondary" data-id="${customer.id}" data-bs-toggle="modal" data-bs-target="#modal-editar-cliente"><i class="bi bi-pencil-square"></i></button>
                <button id="botao-desativar-status-${customer.id}" class="botao-desativar-status btn btn-danger" data-id="${customer.id}" data-name="${customer.name}" data-bs-toggle="modal" data-bs-target="#modal-desativar-status"><i class="bi bi-archive"></i></button>
            </td>
        `;
        table.appendChild(row);
        
        if (!customer.status || !customer.id) {
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
};

const add_notification = (message) => {
    const toasts_container = document.getElementById('toasts-container');

    const toast = `
        <div id="notification" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <strong class="me-auto">Sistema</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                <p>${message}</p>
            </div>
        </div>
    `
    
    toasts_container.innerHTML = toast;

    Array.from(toasts_container.children).forEach(element => {
        bootstrap.Toast.getOrCreateInstance(element).show();
    });
};


/* Funções API */

const load_customers = async (page) => {
    try {
        const response = await fetch(`/api/customers?page${current_page}&per_page=${per_page}`);
        const data = await response.json();
        const customers = Array.from(data.customers);

        total = data.pages;
        customers_on_screen = data.on_screen;

        if (customers.length === 0) {
            table.innerHTML = '<tr><td colspan="6">Nenhum cliente cadastrado ou ativo no sistema.</td></tr>';
            return;
        }

        render_customers(customers);
        current_page = page;
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

        if (customers.length === 0) {
            table.innerHTML = '<tr><td colspan="6">Nenhum cliente encontrado.</td></tr>';
            return;
        }
        
        render_customers(customers);
    } catch (e) {
        console.error(`Erro na pesquisa - ${e}`);
    };
};


const fetch_api = async (route, method, json_data) => {
    const response = await fetch(route,  {
        method : method,
        headers : {
            'Content-Type' : 'application/json',
            'X-CSRFToken' : json_data.csrf_token
        },
        body : JSON.stringify(json_data)
    });

    const data = await response.json();

    if (response.ok) {
        localStorage.setItem('notification', data.message);
        window.location.href = location.href;
    } else {
        add_notification(data.message);
    }
};

const enable_status = (event) => {
    event.preventDefault();

    const form = document.getElementById('FormReativarStatus');
    const formData = new FormData(form);

    fetch_api(
        route = `/api/customers/enable-status/${formData.get('id-reativar-cliente')}`,
        method = 'PATCH',
        json_data = {
            csrf_token : formData.get('csrf_token'),
            id : formData.get('id-reativar-cliente')
        }
    )

    form.reset()
};

const disable_status = (event) => {
    event.preventDefault();

    const form = document.getElementById('FormDesativarStatus');
    const formData = new FormData(form);

    fetch_api(
        route = `/api/customers/disable-status/${formData.get('id-desativar-status')}`,
        method = 'PATCH',
        json_data = {
            csrf_token : formData.get('csrf_token'),
            id : formData.get('id-desativar-status')
        }
    )

    form.reset()
};

const edit_customer = (event) => {
    event.preventDefault()

    const form = document.getElementById('FormEditarCliente');
    const formData = new FormData(form);

    fetch_api(
        route = `/api/customers/edit/${formData.get('id-editar-cliente')}`,
        method = 'PUT',
        json_data = {
            csrf_token : formData.get('csrf_token'),
            id : formData.get('id-editar-cliente'),
            name : formData.get('nome-editar-cliente'),
            cpf : formData.get('cpf-editar-cliente'),
            email : formData.get('email-editar-cliente'),
            address : formData.get('endereco-editar-cliente')
        }
    )

    form.reset()
}


document.addEventListener('DOMContentLoaded', async () => {
    await load_customers();

    const message = localStorage.getItem('notification');
    if (message) {
        add_notification(message);
        localStorage.removeItem('notification');
    }

    // Restrição administrativa para reativar usuário
    if (['admin', 'master'].includes(user_role)) {
        document.getElementById('FormReativarStatus').addEventListener('submit', (event) => enable_status(event));
    }

    // Caso tenham usuários renderizados
    if (customers_on_screen) {
        // Desativar status
        document.getElementById('FormDesativarStatus').addEventListener('submit', (event) => disable_status(event));
        document.getElementById('FormEditarCliente').addEventListener('submit', (event) => edit_customer(event));
    }
    
    /* Pesquisa */ 
    document.getElementById('botao-pesquisa').addEventListener('click', () => search_clients());
    
    /* Botões de Paginação*/
    document.getElementById('botao-anterior').addEventListener('click', () => {
        if (current_page>1) {
            current_page--;
            load_customers(current_page);
        }
    });
    document.getElementById('botao-proxima').addEventListener('click', () => {
        if (current_page<total){
            current_page++;
            load_customers(current_page);
        }
    });
});