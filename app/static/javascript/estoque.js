let total;
let current_page = 1;
const per_page = 10;
const table = document.getElementById('body-tabela-estoque')

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
                    <button id="editar-${product.id}" type="button">E</button>
                    <button id="remover-${product.id}" type="button">R</button>
                </td>
            `;
            table.appendChild(row);
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
                    <button id="editar-${product.id}" type="button">E</button>
                    <button id="remover-${product.id}" type="button">R</button>
                </td>
            `;
            table.appendChild(row);
        });
    }
    catch (error) {
        console.error('Erro na pesquisa de produtos: ', error)
    };
};

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