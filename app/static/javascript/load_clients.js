let total;
let current_page = 1;
const per_page = 10;
const table = document.getElementById('body-tabela-clientes');

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
                    <button class="botao-editar-cliente btn btn-secondary">E</button>
                    <button class="botao-deletar-cliente btn btn-danger">D</button>
                </td>
            `;
            table.appendChild(row);
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
        console.log(customers)

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
                    <button class="botao-editar-cliente btn btn-secondary">E</button>
                    <button class="botao-deletar-cliente btn btn-danger">D</button>
                </td>
            `;
            table.appendChild(row);
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