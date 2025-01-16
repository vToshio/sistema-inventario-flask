const productsContainer = document.getElementById('container-produtos');
const addProductButton = document.getElementById('add-product');
let index = 0;
 
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

document.addEventListener('DOMContentLoaded', () => {
    addProductField();
    addProductButton.addEventListener('click', addProductField);
});