const user_role = document.getElementById('user_role').value;
const logged_user = document.getElementById('logged_user').value;
const table = document.getElementById('body-tabela-usuarios');
let users_on_screen;
let total;
let current_page = 1;
const per_page = 10;
 
/* HELPERS */
const disable_button = (button_id) => {
    document.getElementById(button_id).classList.add('disabled');
};

const enable_button = (button_id) => {
    document.getElementById(button_id).classList.remove('disabled');
};

const handleClickChangePasswd = (event, {title_id, input_id, title}) => {
    const id = event.currentTarget.dataset.id;
    document.getElementById(input_id).value = id;
    document.getElementById(title_id).textContent = title;
};

const handleClickDisable = (event, {title_id, input_id, prefix}) => {
    const id = event.currentTarget.dataset.id;
    const username = event.currentTarget.dataset.username;

    document.getElementById(title_id).textContent = `${prefix} ${username}`;
    document.getElementById(input_id).value = id;
};

const handleClickEdit = async (event, {title_id, input_id, title}) => {
    const id = event.currentTarget.dataset.id;
    const response = await fetch(`/api/users/${id}`);
    const user = await response.json();

    document.getElementById(title_id).textContent = `${title}`;

    document.getElementById(input_id).value = id;
    document.getElementById('nome-editar-usuario').value = user.name;
    document.getElementById('username-editar-usuario').value = user.username;
    document.getElementById('email-editar-usuario').value = user.email;
};

const handleClickRole = async (event, {title_id, input_id, select_id, prefix}) => {
    const id = event.currentTarget.dataset.id;
    const response = await fetch(`/api/users/${id}`);
    const user = await response.json();
    
    document.getElementById(input_id).value = id;
    document.getElementById(select_id).value = user.role_id;
    document.getElementById(title_id).textContent = `${prefix} ${user.username}`;
};

const attach_event_listeners = (class_name, handler, handler_args) => {
    const buttons = document.getElementsByClassName(class_name);

    Array.from(buttons).forEach(btn => {
        btn.removeEventListener('click', handler);
        btn.addEventListener('click', (event) => handler(event, handler_args));
    });
};

const render_users = (users) => {
    table.innerHTML = '';

    users.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <tr class="text-center">
                <td scope="col">${user.id}</td>
                <td scope="col">${user.name}</td>
                <td scope="col">${user.username}</td>
                <td scope="col">${user.role}</td>
                <td scope="col">${user.email}</td>
                <td scope="col">${user.date_created}</td>
                <td scope="col">
                    <button id="botao-mudar-senha-${user.id}" class="botao-mudar-senha btn btn-secondary" data-bs-toggle="modal" data-bs-target="#modal-mudar-senha" data-id="${user.id}" type="button"><i class="bi bi-key-fill"></i></button>
                    <button id="botao-editar-usuario-${user.id}" class="botao-editar-usuario btn btn-secondary" data-bs-toggle="modal" data-bs-target="#modal-editar-usuario" data-id="${user.id}" type="button"><i class="bi bi-pencil-square"></i></button>
                    <button id="botao-editar-cargo-${user.id}" class="botao-editar-cargo btn btn-secondary disabled" data-bs-toggle="modal" data-bs-target="#modal-editar-cargo" data-id="${user.id}" data-user-id="${user.role_id}" type="button"><i class="bi bi-gear-fill"></i></button>
                    <button id="botao-desativar-status-${user.id}" class="botao-desativar-status btn btn-danger" data-bs-toggle="modal" data-bs-target="#modal-desativar-status" data-id="${user.id}" data-username="${user.username}" type="button"><i class="bi bi-archive"></i></button>
                </td>
            </tr>
        `;

        table.appendChild(row);
        
        if (!user.status || user.role === 'Master' || (user.username != logged_user && user.role === user_role)) {
            disable_button(`botao-mudar-senha-${user.id}`);
            disable_button(`botao-editar-usuario-${user.id}`);
            disable_button(`botao-desativar-status-${user.id}`);
        }
        else if (user_role === 'Master') {
            enable_button(`botao-editar-cargo-${user.id}`);
        } 
        else if (user.username === logged_user) {
            disable_button(`botao-desativar-status-${user.id}`);
        }
    });

    attach_event_listeners('botao-desativar-status', handleClickDisable, {
        title_id : 'titulo-modal-desativar-status',
        input_id : 'id-desativar-status',
        prefix : 'Desativar'
    });
    
    attach_event_listeners('botao-mudar-senha', handleClickChangePasswd, {
        title_id : 'titulo-modal-mudar-senha',
        input_id : 'id-mudar-senha',
        title : 'Mudar Senha'
    });

    attach_event_listeners('botao-editar-usuario', handleClickEdit, {
        title_id : 'titulo-modal-editar-usuario',
        input_id : 'id-editar-usuario',
        title : 'Editar Usuário'
    });

    attach_event_listeners('botao-editar-cargo', handleClickRole, {
        title_id : 'titulo-modal-editar-cargo',
        input_id : 'id-editar-cargo',
        select_id : 'select-editar-cargo',
        prefix : 'Editar Cargo'
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

const load_users = async (page) => {
    try {
        const response = await fetch(`/api/users?page=${current_page}&per_page=${per_page}`);
        const data = await response.json();
        const users = Array.from(data.users);

        total = data.pages;
        users_on_screen = data.on_screen;

        if (users.length === 0) {
            table.innerHTML = '<tr><td colspan="7">Nenhum usuário cadastrado ou ativo no sistema.</td></tr>';
            return;
        }

        render_users(users);
        current_page = page;
    } catch (e) {
        console.error('Erro ao pesquisar usuários - ', e);
    }
};

const search_users = async () => {
    try {
        const query = document.getElementById('barra-pesquisa').value;
        const response = await fetch(`/api/users/search?query=${query}`);
        const data = await response.json();
        const users = Array.from(data.users);

        table.innerHTML = '';

        if (users.length === 0) {
            table.innerHTML = '<tr><td colspan="7">Nenhum usuário encontrado.</td></tr>';
            return;
        }

        render_users(users);
    } catch (e) {
        console.error('Erro ao pesquisar usuário - ', e);
    }
};

const fetch_api = async(route, method, json_data) => {
    const response = await fetch(route , {
        method : method,
        headers : {
            'Content-Type' : 'application/json',
            'X-CSRFToken': json_data.csrf_token
        },
        body : JSON.stringify(json_data)
    })

    const data = await response.json();

    if (response.ok) {
        localStorage.setItem('notification', data.message);
        window.location.href = location.href;
    } else {
        add_notification(data.message);
    }
}

const change_passwd = (event) => {
    event.preventDefault();

    const form = document.getElementById('FormMudarSenha');
    const formData = new FormData(form);

    fetch_api(
        route = `/api/users/change-password/${formData.get('id-mudar-senha')}`,
        method = 'PATCH',
        json_data = {
            'csrf_token' : formData.get('csrf_token'),
            'id' : formData.get('id-mudar-senha'),
            'new_password' : formData.get('nova-senha-usuario'),
            'confirm' : formData.get('confirmar-nova-senha'),
        }
    );

    form.reset()
}

const edit_user = (event) => {
    event.preventDefault();

    const form = document.getElementById('FormEditarUsuario');
    const formData = new FormData(form);

    fetch_api(
        route = `/api/users/edit/${formData.get('id-editar-usuario')}`,
        method = 'PUT',
        json_data = {
            csrf_token : formData.get('csrf_token'),
            id : formData.get('id-editar-usuario'),
            name : formData.get('nome-editar-usuario'),
            username : formData.get('username-editar-usuario'),
            email : formData.get('email-editar-usuario')
        }
    );

    form.reset();
}; 

const edit_role = (event) => {
    event.preventDefault();

    const form = document.getElementById('FormEditarCargo');
    const formData = new FormData(form);

    fetch_api(
        route = `/api/users/edit-role/${formData.get('id-editar-cargo')}`,
        method = 'PATCH',
        json_data = {
            csrf_token : formData.get('csrf_token'),
            id : formData.get('id-editar-cargo'),
            role_id : formData.get('select-editar-cargo')
        }
    )

    form.reset()
};

const disable_status = (event) => {
    event.preventDefault();

    const form = document.getElementById('FormDesativarStatus');
    const formData = new FormData(form);

    fetch_api(
        route = `/api/users/disable-status/${formData.get('id-desativar-status')}`,
        method = 'PATCH',
        json_data = {
            csrf_token : formData.get('csrf_token'),
            id : formData.get('id-desativar-status'),
        }
    )

    form.reset()
};

const enable_status = (event) => {
    event.preventDefault();

    const form = document.getElementById('FormReativarStatus');
    const formData = new FormData(form);

    fetch_api(
        route = `/api/users/enable-status/${formData.get('id-ativar-status')}`,
        method = 'PATCH',
        json_data = {
            csrf_token : formData.get('csrf_token'),
            id : formData.get('id-ativar-status'),
        }
    )

    form.reset()
};

document.addEventListener('DOMContentLoaded', async () => {
    await load_users(current_page);

    const message = localStorage.getItem('notification');
    if (message) {
        add_notification(message);
        localStorage.removeItem('notification');
    }

    if (users_on_screen) {
        // Form Mudar Senha
        document.getElementById('FormMudarSenha').addEventListener('submit', (event) => change_passwd(event));
        
        // Form Editar Usuário
        document.getElementById('FormEditarUsuario').addEventListener('submit', (event) => edit_user(event));

        // Form Editar Cargo
        document.getElementById('FormEditarCargo').addEventListener('submit', (event) => edit_role(event));

        // Form Desativar Usuário
        document.getElementById('FormDesativarStatus').addEventListener('submit', (event) => disable_status(event));    
    
    }
    
    // Form Reativar Usuário
    document.getElementById('FormReativarStatus').addEventListener('submit', (event) => enable_status(event));
    
    /* Pesquisa */
    document.getElementById('botao-pesquisa').addEventListener('click', () => search_users());    

    /* Paginação */
    document.getElementById('botao-anterior').addEventListener('click', () => {
        if (current_page>1) {
            current_page--;
            load_users(current_page);
        }
    });
    document.getElementById('botao-proxima').addEventListener('click', () => {
        if (current_page<total){
            current_page++;
            load_users(current_page);
        };
    });
});