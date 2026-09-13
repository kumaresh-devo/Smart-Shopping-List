/**
 * Dashboard JavaScript handlers
 */

document.addEventListener('DOMContentLoaded', () => {
  const quickAddModal = document.getElementById('quickAddModal');
  if (quickAddModal) {
    quickAddModal.addEventListener('show.bs.modal', (event) => {
      const button = event.relatedTarget;
      if (!button) return;

      const itemName = button.getAttribute('data-item-name') || '';
      const category = button.getAttribute('data-category') || 'Other';
      const avgPrice = button.getAttribute('data-price') || '0.00';

      const inputName = quickAddModal.querySelector('#modal_item_name');
      const inputCategory = quickAddModal.querySelector('#modal_category');
      const inputPrice = quickAddModal.querySelector('#modal_price');

      if (inputName) inputName.value = itemName;
      if (inputCategory) inputCategory.value = category;
      if (inputPrice) inputPrice.value = avgPrice;
    });
  }
});
