const productsContainer = document.getElementById('container-produtos');
const addProductButton = document.getElementById('add-product');
const table = document.getElementById('body-tabela-vendas');
let index = 0;
let total;
let current_page = 1;
const per_page = 10;
 
const addProductField = () => {
    const productField = document.createElement('div');
    productField.classList.add('product-field', 'mb-3');
    productField.innerHTML = `
        <div class="row">
            <div class="col">
                <input type="number" name="products-${index}-id" id="products-${index}-id" class="form-control" placeholder="ID do Produto" required>
            </div>
            <div class="col">
                <input type="number" name="products-${index}-quantity" id="products-${index}-quantity" class="form-control" placeholder="Quantidade de Produtos" required>
            </div>
            <div class="col-auto d-flex align-items-end">
                <button type="button" class="botao-remover-produto btn btn-danger">Remover</button>
            </div>
        </div>
    `;
    productsContainer.appendChild(productField);

    productField.querySelector('.botao-remover-produto').addEventListener('click', () => {
        productField.remove();
    });

    index++;
};

const handleDownload = async () => {
    console.log('teste');
};

const attach_event_listeners = (class_name, handler, handler_args) => {
    const buttons = document.getElementsByClassName(class_name);

    Array.from(buttons).forEach(btn => {
        btn.removeEventListener('click');
        btn.addEventListener('click', () => handler(handler_args));
    });
};

const load_sales = async (page) => {
    try {
        const response = await fetch(`/api/sales?page=${page}&per_page=${per_page}`);
        const data = await response.json();
        const sales = Array.from(data.sales);

        total = data.pages;
        table.innerHTML = '';

        if (data.total === 0) {
            table.innerHTML = '<tr><td colspan="6">Nenhuma venda cadastrada no sistema.</td></tr>';
            return;
        }

        sales.forEach(sale => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td scope="col">${sale.id}</td>
                <td scope="col">${sale.customer}</td>
                <td scope="col">${sale.salesman}</td>
                <td scope="col">${sale.sell_date}</td>
                <td scope="col">${sale.total}</td>
                <td scope="col">
                    <button class="botao-download btn btn-success" type="button">Download</button>
                </td>
            `;
            table.appendChild(row);
        });
        current_page = page;
    }
    catch (error) {
        console.error('Erro no carregamento das vendas: ', error);
    }
};

const search_sales = async () => {
    const query = document.getElementById('barra-pesquisa').value;
    const response = await fetch(`/api/sales/search?query=${query}`);
    const data = await response.json();
    const sales = Array.from(data.sales);

    table.innerHTML = ''

    if (sales.length === 0) {
        table.innerHTML = '<tr><td colspan="6">Nenhuma venda encontrada.</td></tr>';
        return;
    }

    sales.forEach(sale => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td scope="col">${sale.id}</td>
            <td scope="col">${sale.customer}</td>
            <td scope="col">${sale.salesman}</td>
            <td scope="col">${sale.sell_date}</td>
            <td scope="col">${sale.total}</td>
            <td scope="col">
                <button class="botao-download btn btn-success" data-id=${sale.id} type="button">Download</button>
            </td>
        `;
        table.appendChild(row);
    });
};

document.getElementById('botao-anterior').addEventListener('click', () => {
    if (current_page>1) {
        current_page--;
        load_sales(current_page);
    }
});

document.getElementById('botao-proxima').addEventListener('click', () => {
    if (current_page<total){
        current_page++;
        load_sales(current_page);
    }
});

document.getElementById('botao-pesquisa').addEventListener('click', () => search_sales());

document.addEventListener('DOMContentLoaded', () => {
    addProductField();
    addProductButton.addEventListener('click', addProductField);
    
    load_sales(current_page);    
    
});