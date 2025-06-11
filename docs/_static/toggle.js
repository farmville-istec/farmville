// Toggle da Sidebar - FarmVille Documentation
document.addEventListener('DOMContentLoaded', function() {
    
    // Criar botão toggle
    const toggleButton = document.createElement('button');
    toggleButton.className = 'sidebar-toggle';
    toggleButton.innerHTML = '☰';
    toggleButton.title = 'Mostrar/Esconder Menu';
    
    // Adicionar botão ao body
    document.body.appendChild(toggleButton);
    
    // Elementos principais
    const sidebar = document.querySelector('.wy-nav-side');
    const content = document.querySelector('.wy-nav-content');
    const header = document.querySelector('.wy-nav-top');
    
    // Estado inicial da sidebar (visível em desktop, escondida em mobile)
    let sidebarVisible = window.innerWidth > 1024;
    
    // Função para atualizar estado da sidebar
    function updateSidebarState() {
        if (sidebarVisible) {
            // Mostrar sidebar
            sidebar.classList.remove('sidebar-hidden');
            content.classList.remove('sidebar-hidden');
            header.classList.remove('sidebar-hidden');
            toggleButton.classList.remove('sidebar-hidden');
            toggleButton.classList.add('sidebar-visible');
            toggleButton.innerHTML = '✕';
            toggleButton.title = 'Esconder Menu';
        } else {
            // Esconder sidebar
            sidebar.classList.add('sidebar-hidden');
            content.classList.add('sidebar-hidden');
            header.classList.add('sidebar-hidden');
            toggleButton.classList.remove('sidebar-visible');
            toggleButton.classList.add('sidebar-hidden');
            toggleButton.innerHTML = '☰';
            toggleButton.title = 'Mostrar Menu';
        }
        
        // Salvar estado no localStorage
        localStorage.setItem('farmville-sidebar-visible', sidebarVisible);
    }
    
    // Restaurar estado salvo
    const savedState = localStorage.getItem('farmville-sidebar-visible');
    if (savedState !== null) {
        sidebarVisible = savedState === 'true';
    }
    
    // Aplicar estado inicial
    updateSidebarState();
    
    // Event listener para o botão toggle
    toggleButton.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        sidebarVisible = !sidebarVisible;
        updateSidebarState();
        
        // Pequena animação no botão
        toggleButton.style.transform = 'scale(0.9)';
        setTimeout(() => {
            toggleButton.style.transform = 'scale(1)';
        }, 150);
    });
    
    // Fechar sidebar ao clicar em links (em mobile)
    if (window.innerWidth <= 1024) {
        const sidebarLinks = sidebar.querySelectorAll('a');
        sidebarLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 1024) {
                    sidebarVisible = false;
                    updateSidebarState();
                }
            });
        });
    }
    
    // Responsive: esconder sidebar automaticamente em mobile
    window.addEventListener('resize', function() {
        if (window.innerWidth <= 1024 && sidebarVisible) {
            sidebarVisible = false;
            updateSidebarState();
        } else if (window.innerWidth > 1024 && !sidebarVisible) {
            sidebarVisible = true;
            updateSidebarState();
        }
    });
    
    // Keyboard shortcut: Ctrl+B para toggle
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'b') {
            e.preventDefault();
            sidebarVisible = !sidebarVisible;
            updateSidebarState();
        }
    });
    
    // Fechar sidebar ao clicar fora dela (apenas em mobile)
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 1024 && sidebarVisible) {
            const isClickInsideSidebar = sidebar.contains(e.target);
            const isToggleButton = e.target === toggleButton;
            
            if (!isClickInsideSidebar && !isToggleButton) {
                sidebarVisible = false;
                updateSidebarState();
            }
        }
    });
    
    // Impedir propagação de cliques dentro da sidebar
    sidebar.addEventListener('click', function(e) {
        e.stopPropagation();
    });
    
    // Melhorar acessibilidade
    toggleButton.setAttribute('aria-label', 'Toggle navigation menu');
    toggleButton.setAttribute('role', 'button');
    
    // Suporte para toque em dispositivos móveis
    let touchStartX = 0;
    let touchEndX = 0;
    
    document.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].screenX;
    });
    
    document.addEventListener('touchend', function(e) {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipeGesture();
    });
    
    function handleSwipeGesture() {
        const swipeThreshold = 100;
        const swipeDistance = touchEndX - touchStartX;
        
        // Swipe da esquerda para a direita (mostrar sidebar)
        if (swipeDistance > swipeThreshold && !sidebarVisible && touchStartX < 50) {
            sidebarVisible = true;
            updateSidebarState();
        }
        
        // Swipe da direita para a esquerda (esconder sidebar)
        if (swipeDistance < -swipeThreshold && sidebarVisible) {
            sidebarVisible = false;
            updateSidebarState();
        }
    }
    
    console.log('🌾 FarmVille Documentation - Sidebar toggle loaded!');
    console.log('💡 Tip: Use Ctrl+B to toggle sidebar or swipe on mobile');
});