/**
 * Shopping History Interactions & Delete Confirmation Modal
 */

document.addEventListener('DOMContentLoaded', () => {
  const deleteHistoryModal = document.getElementById('deleteHistoryModal');
  if (deleteHistoryModal) {
    deleteHistoryModal.addEventListener('show.bs.modal', (event) => {
      const button = event.relatedTarget;
      if (!button) return;

      const recordId = button.getAttribute('data-record-id');
      const itemName = button.getAttribute('data-item-name');
      const price = button.getAttribute('data-price');
      const date = button.getAttribute('data-date');

      const form = deleteHistoryModal.querySelector('#deleteHistoryForm');
      const nameElem = deleteHistoryModal.querySelector('#delete_history_item_name');
      const priceElem = deleteHistoryModal.querySelector('#delete_history_price');
      const dateElem = deleteHistoryModal.querySelector('#delete_history_date');

      if (form) form.action = `/history/${recordId}/delete`;
      if (nameElem) nameElem.textContent = `"${itemName}"`;
      if (priceElem) priceElem.textContent = price || '0.00';
      if (dateElem) dateElem.textContent = date || '';
    });
  }
});
