const handleClickChangePasswd = (event, {title_id, input_id, title}) => {
    const id = event.target.dataset.id;
    document.getElementById(input_id).value = id;
    document.getElementById(title_id).textContent = title;
};

const handleClickDelete = (event, {title_id, input_id, prefix}) => {
    const id = event.target.dataset.id;
    const username = event.target.dataset.username;

    document.getElementById(title_id).textContent = `${prefix} ${username}`;
    document.getElementById(input_id).value = id;
};

const handleClickEdit = async (event, {title_id, input_id, title}) => {
    const id = event.target.dataset.id;
    const response = await fetch(`/api/users/${id}`);
    const user = await response.json();
    console.log(user);

    document.getElementById(title_id).textContent = `${title}`;

    document.getElementById(input_id).value = id;
    document.getElementById('nome-editar-usuario').value = user.name;
    document.getElementById('username-editar-usuario').value = user.username;
    document.getElementById('select-editar-usuario').value = user.role_id;
    document.getElementById('email-editar-usuario').value = user.email;
};

const attach_event_listeners = (class_name, handler, handler_args) => {
    const buttons = document.getElementsByClassName(class_name);

    Array.from(buttons).forEach(btn => {
        btn.removeEventListener('click', handler);
        btn.addEventListener('click', (event) => handler(event, handler_args));
    });
};

document.addEventListener('DOMContentLoaded', () => {
    attach_event_listeners('botao-deletar-usuario', handleClickDelete, {
        title_id : 'titulo-modal-deletar-usuario',
        input_id : 'id-deletar-usuario',
        prefix : 'Deletar'
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
});