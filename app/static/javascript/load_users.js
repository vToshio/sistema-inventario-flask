const user_role = document.getElementById('user_role').value;
const logged_user = document.getElementById('logged_user').value;
const table = document.getElementById('body-tabela-usuarios');
let total;
let current_page = 1;
const per_page = 10;
 

const disable_button = (button_id) => {
    document.getElementById(button_id).classList.add('disabled');
};

const enable_button = (button_id) => {
    document.getElementById(button_id).classList.remove('disabled');
};

const handleClickChangePasswd = (event, {title_id, input_id, title}) => {
    const id = event.target.dataset.id;
    document.getElementById(input_id).value = id;
    document.getElementById(title_id).textContent = title;
};

const handleClickDisable = (event, {title_id, input_id, prefix}) => {
    const id = event.target.dataset.id;
    const username = event.target.dataset.username;

    document.getElementById(title_id).textContent = `${prefix} ${username}`;
    document.getElementById(input_id).value = id;
};

const handleClickEdit = async (event, {title_id, input_id, title}) => {
    const id = event.target.dataset.id;
    const response = await fetch(`/api/users/get/${id}`);
    const user = await response.json();

    document.getElementById(title_id).textContent = `${title}`;

    document.getElementById(input_id).value = id;
    document.getElementById('nome-editar-usuario').value = user.name;
    document.getElementById('username-editar-usuario').value = user.username;
    document.getElementById('email-editar-usuario').value = user.email;
};

const handleClickRole = async (event, {title_id, input_id, select_id, prefix}) => {
    const id = event.target.dataset.id;
    const role_id = event.target.dataset.role_id
    const response = await fetch(`/api/users/get/${id}`);
    const user = await response.json();
    
    document.getElementById(input_id).value = id;
    document.getElementById(select_id).value = role_id;
    document.getElementById(title_id).textContent = `${prefix} ${user.username}`;
    document.getElementById('select-editar-cargo').value = user.role_id;
};

const attach_event_listeners = (class_name, handler, handler_args) => {
    const buttons = document.getElementsByClassName(class_name);

    Array.from(buttons).forEach(btn => {
        btn.removeEventListener('click', handler);
        btn.addEventListener('click', (event) => handler(event, handler_args));
    });
};

const load_users = async (page) => {
    try {
        const response = await fetch(`/api/users/get?page=${current_page}&per_page=${per_page}`);
        const data = await response.json();
        const users = Array.from(data.users);

        total = data.pages;
        table.innerHTML = '';

        if (users.length === 0) {
            table.innerHTML = '<tr><td colspan="7">Nenhum usuário cadastrado ou ativo no sistema.</td></tr>';
            return;
        }

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
                        <button id="botao-mudar-senha-${user.id}" class="botao-mudar-senha btn btn-secondary" data-bs-toggle="modal" data-bs-target="#modal-mudar-senha" data-id="${user.id}" type="button">P</button>
                        <button id="botao-editar-usuario-${user.id}" class="botao-editar-usuario btn btn-secondary" data-bs-toggle="modal" data-bs-target="#modal-editar-usuario" data-id="${user.id}" type="button">E</button>
                        <button id="botao-editar-cargo-${user.id}" class="botao-editar-cargo btn btn-secondary disabled" data-bs-toggle="modal" data-bs-target="#modal-editar-cargo" data-id="${user.id}" data-user-id="${user.role_id}" type="button">ER</button>
                        <button id="botao-desativar-status-${user.id}" class="botao-desativar-status btn btn-danger" data-bs-toggle="modal" data-bs-target="#modal-desativar-status" data-id="${user.id}" data-username="${user.username}" type="button">D</button>
                    </td>
                </tr>
            `;

            table.appendChild(row);
            
            
            if (user_role === 'Master') {
                enable_button(`botao-editar-cargo-${user.id}`);
            } else {
                if (logged_user === user.username) {
                    disable_button(`botao-desativar-status-${user.id}`);
                }
    
                if (logged_user != user.username && user.role === 'Admin' && user_role != 'master') {
                    disable_button(`botao-mudar-senha-${user.id}`);
                    disable_button(`botao-editar-usuario-${user.id}`);
                    disable_button(`botao-desativar-status-${user.id}`);
                }
            }
        });
        
        current_page = page;
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
                    <button id="botao-mudar-senha-${user.id}" class="botao-mudar-senha btn btn-secondary" data-bs-toggle="modal" data-bs-target="#modal-mudar-senha" data-id="${user.id}" type="button">P</button>
                    <button id="botao-editar-usuario-${user.id}" class="botao-editar-usuario btn btn-secondary" data-bs-toggle="modal" data-bs-target="#modal-editar-usuario" data-id="${user.id}" type="button">E</button>
                    <button id="botao-editar-cargo-${user.id}" class="botao-editar-cargo btn btn-secondary disabled" data-bs-toggle="modal" data-bs-target="#modal-editar-cargo" data-id="${user.id}" data-user-id="${user.role_id}" type="button">ER</button>
                    <button id="botao-desativar-status-${user.id}" class="botao-desativar-status btn btn-danger" data-bs-toggle="modal" data-bs-target="#modal-desativar-status" data-id="${user.id}" data-username="${user.username}" type="button">D</button>
                </td>
            </tr>`;

            table.appendChild(row);
            
            
            if (user_role === 'Master' && user.status) {
                if (user.role === 'Master'){
                    disable_button(`botao-mudar-senha-${user.id}`);
                    disable_button(`botao-editar-usuario-${user.id}`);
                    disable_button(`botao-desativar-status-${user.id}`);
                }
                else 
                    enable_button(`botao-editar-cargo-${user.id}`);
            } 
            else {
                if (!user.status || user.role === 'Master') {
                    disable_button(`botao-mudar-senha-${user.id}`);
                    disable_button(`botao-editar-usuario-${user.id}`);
                    disable_button(`botao-desativar-status-${user.id}`);
                }
                else if (logged_user === user.username) {
                    disable_button(`botao-desativar-status-${user.id}`);
                }
                else if (user.role === 'Admin'){
                    disable_button(`botao-mudar-senha-${user.id}`);
                    disable_button(`botao-editar-usuario-${user.id}`);
                    disable_button(`botao-desativar-status-${user.id}`);
                }
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
            prefix : 'Editar Cargo'
        });
    } catch (e) {
        console.error('Erro ao pesquisar usuário - ', e);
    }
};

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

document.addEventListener('DOMContentLoaded', () => {
    load_users(current_page);
    document.getElementById('botao-pesquisa').addEventListener('click', () => search_users());    
});