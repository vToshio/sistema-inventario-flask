const table = document.getElementById('body-tabela-usuarios');
const role = sessionStorage.getItem('user_role');

/*
const load_users = async () => {
    const response = await fetch('/api/users/get');
    const data = await response.json();
    table.innerHTML = '';

    if ((!data.users)) {
        table.innerHTML = '<tr><td colspan="7">Nenhum usuário foi cadastrado.</td></tr>'
    }
    
    Array.from(data.users).forEach(user => {
        let row = document.createElement('tr');
        row.innerHTML = `
            <td scope="col">${user.id}</td>
            <td scope="col">${user.name}</td>
            <td scope="col">${user.username}</td>
            <td scope="col">${user.role}</td>
            <td scope="col">${user.email}</td>
            <td scope="col">${user.date_created}</td>
            <td scope="col">
                <button class="btn btn-secondary">P</button>
                <button class="btn btn-secondary">E</button>
                <button class="btn btn-danger">D</button>
            </td>
        `;
        table.appendChild(row);
    });
};
*/

const search_users = async () => {
    const query = document.getElementById('barra-pesquisa').value;
    const response = await fetch(`/api/users/search?query=${query}`);
    const data = await response.json();
    table.innerHTML = '';

    if (data.users.length === 0) {
        table.innerHTML = '<tr><td colspan="7">Nenhum usuário foi encontrado.</td></tr>'
        return;
    }
    
    Array.from(data.users).forEach(user => {
        let row = document.createElement('tr');
        row.innerHTML = `
            <td scope="col">${user.id}</td>
            <td scope="col">${user.name}</td>
            <td scope="col">${user.username}</td>
            <td scope="col">${user.role}</td>
            <td scope="col">${user.email}</td>
            <td scope="col">${user.date_created}</td>
            <td scope="col">
                <button class="btn btn-secondary">P</button>
                <button class="btn btn-secondary">E</button>
                <button class="btn btn-danger">D</button>
            </td>
        `;
        table.appendChild(row);
    });
};

document.getElementById('botao-pesquisa').addEventListener('click', () => search_users());

document.addEventListener('DOMContentLoaded', () => load_users());