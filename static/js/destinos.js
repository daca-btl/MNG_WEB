document.addEventListener('DOMContentLoaded', function () {
    const cards = Array.from(document.querySelectorAll('.tarjeta-tour'));
    const button = document.getElementById('btn-ver-mas-tours');

    if (!cards.length || !button) {
        return;
    }

    const pageSize = 6;
    let visibleCount = pageSize;

    const applyVisibility = () => {
        cards.forEach((card, index) => {
            const shouldShow = index < visibleCount;
            card.classList.toggle('is-hidden', !shouldShow);
            card.style.display = shouldShow ? '' : 'none';
        });

        button.classList.toggle('d-none', visibleCount >= cards.length);
        button.innerHTML = visibleCount >= cards.length
            ? '<i class="bi bi-check-circle me-2"></i>Mostrando todos'
            : '<i class="bi bi-chevron-down me-2"></i>Ver más';
    };

    cards.forEach((card, index) => {
        if (index >= pageSize) {
            card.classList.add('is-hidden');
            card.style.display = 'none';
        }
    });

    button.addEventListener('click', function () {
        if (visibleCount + pageSize >= cards.length) {
            visibleCount = cards.length;
        } else {
            visibleCount += pageSize;
        }

        applyVisibility();
    });

    applyVisibility();
});
