/**
 * Add Item Page Validation
 */

document.addEventListener('DOMContentLoaded', () => {
  const addItemForm = document.getElementById('addItemForm');
  if (addItemForm) {
    addItemForm.addEventListener('submit', (e) => {
      const quantityInput = document.getElementById('quantity');
      const priceInput = document.getElementById('estimated_price');

      if (quantityInput && parseFloat(quantityInput.value) <= 0) {
        alert('Quantity must be greater than zero.');
        e.preventDefault();
        quantityInput.focus();
        return;
      }

      if (priceInput && parseFloat(priceInput.value) < 0) {
        alert('Estimated price cannot be negative.');
        e.preventDefault();
        priceInput.focus();
        return;
      }
    });
  }

  const itemAddedModal = document.getElementById('itemAddedModal');
  if (itemAddedModal) {
    const modal = new bootstrap.Modal(itemAddedModal);
    modal.show();

    const addAnotherItemButton = document.getElementById('addAnotherItemButton');
    if (addAnotherItemButton) {
      addAnotherItemButton.addEventListener('click', () => {
        const selectedListId = document.getElementById('list_id').value;
        addItemForm.reset();
        document.getElementById('list_id').value = selectedListId;
        modal.hide();
      });
    }
  }
});
