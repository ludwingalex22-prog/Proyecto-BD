// Esto es opcional: si quieres cerrar menú al hacer clic en un link (Bootstrap ya lo hace automáticamente en la mayoría)
document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('.navbar-nav .nav-link');
    const collapse = document.getElementById('navbarNav');
    links.forEach(link => {
        link.addEventListener('click', () => {
            if (collapse.classList.contains('show')) {
                new bootstrap.Collapse(collapse).toggle();
            }
        });
    });
});
