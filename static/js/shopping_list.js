/**
 * Shopping List Page Interactions & Filtering
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Filtering & Live Search
  const searchInput = document.getElementById('itemSearchInput');
  const categoryFilter = document.getElementById('categoryFilter');
  const statusFilter = document.getElementById('statusFilter');
  const itemsTable = document.getElementById('itemsTable');
  const noMatchingAlert = document.getElementById('noMatchingItems');

  function filterItems() {
    if (!itemsTable) return;

    const searchTerm = (searchInput ? searchInput.value : '').toLowerCase().trim();
    const selectedCategory = categoryFilter ? categoryFilter.value : 'all';
    const selectedStatus = statusFilter ? statusFilter.value : 'all';

    const rows = itemsTable.querySelectorAll('tbody tr.item-row');
    let visibleCount = 0;

    rows.forEach((row) => {
      const name = (row.getAttribute('data-name') || '').toLowerCase();
      const category = row.getAttribute('data-category') || '';
      const status = row.getAttribute('data-status') || '';

      const matchesSearch = !searchTerm || name.includes(searchTerm);
      const matchesCategory = selectedCategory === 'all' || category === selectedCategory;
      const matchesStatus = selectedStatus === 'all' || status === selectedStatus;

      if (matchesSearch && matchesCategory && matchesStatus) {
        row.style.display = '';
        visibleCount++;
      } else {
        row.style.display = 'none';
      }
    });

    if (noMatchingAlert) {
      if (visibleCount === 0 && rows.length > 0) {
        noMatchingAlert.classList.remove('d-none');
      } else {
        noMatchingAlert.classList.add('d-none');
      }
    }
  }

  if (searchInput) searchInput.addEventListener('input', filterItems);
  if (categoryFilter) categoryFilter.addEventListener('change', filterItems);
  if (statusFilter) statusFilter.addEventListener('change', filterItems);

  // 2. Share List
  const shareListButton = document.getElementById('shareListButton');
  if (shareListButton) {
    const copyListButton = document.getElementById('copyListButton');
    const whatsappListButton = document.getElementById('whatsappListButton');
    const shareListSuccess = document.getElementById('shareListSuccess');

    const getListText = () => {
      const items = Array.from(document.querySelectorAll('#itemsTable tbody tr.item-row'))
        .map((row) => `- ${row.getAttribute('data-share-name')}: ${row.getAttribute('data-share-quantity')}`);
      return [
        shareListButton.getAttribute('data-list-title'),
        '',
        ...(items.length ? items : ['No items']),
        '',
        `Estimated total: ₹${parseFloat(shareListButton.getAttribute('data-estimated-total') || 0).toFixed(2)}`
      ].join('\n');
    };

    if (copyListButton) {
      copyListButton.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(getListText());
        if (shareListSuccess) {
          shareListSuccess.classList.remove('d-none');
          setTimeout(() => shareListSuccess.classList.add('d-none'), 2000);
        }
      } catch (error) {
        console.error('Unable to copy list.', error);
      }
      });
    }

    if (whatsappListButton) {
      whatsappListButton.addEventListener('click', () => {
        window.open(`https://wa.me/?text=${encodeURIComponent(getListText())}`, '_blank', 'noopener');
      });
    }
  }

  // 3. Edit List Modal
  const editListModal = document.getElementById('editListModal');
  if (editListModal) {
    editListModal.addEventListener('show.bs.modal', (event) => {
      const button = event.relatedTarget;
      if (!button) return;
      const listId = button.getAttribute('data-list-id');
      const listTitle = button.getAttribute('data-list-title');

      const form = editListModal.querySelector('#editListForm');
      const titleInput = editListModal.querySelector('#edit_list_title');

      if (form) form.action = `/lists/${listId}/edit`;
      if (titleInput) titleInput.value = listTitle || '';
    });
  }

  // 3. Delete List Modal
  const deleteListModal = document.getElementById('deleteListModal');
  if (deleteListModal) {
    deleteListModal.addEventListener('show.bs.modal', (event) => {
      const button = event.relatedTarget;
      if (!button) return;
      const listId = button.getAttribute('data-list-id');
      const listTitle = button.getAttribute('data-list-title');

      const form = deleteListModal.querySelector('#deleteListForm');
      const nameElem = deleteListModal.querySelector('#delete_list_name');

      if (form) form.action = `/lists/${listId}/delete`;
      if (nameElem) nameElem.textContent = `"${listTitle}"`;
    });
  }

  // 4. Edit Item Modal
  const editItemModal = document.getElementById('editItemModal');
  if (editItemModal) {
    editItemModal.addEventListener('show.bs.modal', (event) => {
      const button = event.relatedTarget;
      if (!button) return;

      const itemId = button.getAttribute('data-item-id');
      const itemName = button.getAttribute('data-item-name');
      const category = button.getAttribute('data-category');
      const quantity = button.getAttribute('data-quantity');
      const unit = button.getAttribute('data-unit');
      const estPrice = button.getAttribute('data-est-price');
      const notes = button.getAttribute('data-notes');

      const form = editItemModal.querySelector('#editItemForm');
      if (form) form.action = `/items/${itemId}/edit`;

      const inputName = editItemModal.querySelector('#edit_item_name');
      const inputCategory = editItemModal.querySelector('#edit_category');
      const inputQuantity = editItemModal.querySelector('#edit_quantity');
      const inputUnit = editItemModal.querySelector('#edit_unit');
      const inputPrice = editItemModal.querySelector('#edit_estimated_price');
      const inputNotes = editItemModal.querySelector('#edit_notes');

      if (inputName) inputName.value = itemName || '';
      if (inputCategory) inputCategory.value = category || 'Other';
      if (inputQuantity) inputQuantity.value = quantity || '1';
      if (inputUnit) inputUnit.value = unit || 'pcs';
      if (inputPrice) inputPrice.value = estPrice || '0.00';
      if (inputNotes) inputNotes.value = notes || '';
    });
  }

  // 5. Purchase Item Modal (Actual price prompt)
  const purchaseModal = document.getElementById('purchaseModal');
  if (purchaseModal) {
    purchaseModal.addEventListener('show.bs.modal', (event) => {
      const button = event.relatedTarget;
      if (!button) return;

      const itemId = button.getAttribute('data-item-id');
      const itemName = button.getAttribute('data-item-name');
      const estPrice = button.getAttribute('data-est-price');

      const form = purchaseModal.querySelector('#purchaseForm');
      const itemNameDisplay = purchaseModal.querySelector('#purchase_item_name');
      const estPriceDisplay = purchaseModal.querySelector('#purchase_est_display');
      const actualPriceInput = purchaseModal.querySelector('#purchase_actual_price');

      if (form) form.action = `/items/${itemId}/purchase`;
      if (itemNameDisplay) itemNameDisplay.textContent = itemName || '';
      if (estPriceDisplay) estPriceDisplay.textContent = `₹${parseFloat(estPrice || 0).toFixed(2)}`;
      if (actualPriceInput) {
        actualPriceInput.value = parseFloat(estPrice || 0).toFixed(2);
        setTimeout(() => actualPriceInput.select(), 300);
      }
    });
  }

  // 6. Delete Item Modal
  const deleteItemModal = document.getElementById('deleteItemModal');
  if (deleteItemModal) {
    deleteItemModal.addEventListener('show.bs.modal', (event) => {
      const button = event.relatedTarget;
      if (!button) return;

      const itemId = button.getAttribute('data-item-id');
      const itemName = button.getAttribute('data-item-name');

      const form = deleteItemModal.querySelector('#deleteItemForm');
      const nameDisplay = deleteItemModal.querySelector('#delete_item_name');

      if (form) form.action = `/items/${itemId}/delete`;
      if (nameDisplay) nameDisplay.textContent = `"${itemName}"`;
    });
  }
});
