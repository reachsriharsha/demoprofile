// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Navbar background on scroll
const navbar = document.querySelector('.navbar');
window.addEventListener('scroll', () => {
    if (window.scrollY > 100) {
        navbar.style.background = 'rgba(10, 14, 26, 0.95)';
        navbar.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.background = 'rgba(10, 14, 26, 0.8)';
        navbar.style.boxShadow = 'none';
    }
});

// Intersection Observer for fade-in animations
const observerOptions = {
    threshold:  0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style. transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all feature cards and other elements
document.querySelectorAll('.feature-card, .tech-category, .highlight-card, .contact-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});

// Counter animation for stats
const animateCounter = (element, target, duration = 2000) => {
    let current = 0;
    const increment = target / (duration / 16);
    const isNumber = ! isNaN(target);
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = isNumber ? Math.ceil(target) : target;
            clearInterval(timer);
        } else {
            element.textContent = isNumber ? Math.ceil(current) : current;
        }
    }, 16);
};

// Trigger counter animation when stats section is visible
const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const statNumbers = document.querySelectorAll('. stat-number');
            statNumbers.forEach(stat => {
                const target = stat.textContent. includes('+') 
                    ? parseInt(stat. textContent) 
                    : parseInt(stat. textContent);
                const suffix = stat.textContent.includes('+') ? '+' : '%';
                
                animateCounter({
                    set textContent(value) {
                        stat.textContent = Math.ceil(value) + (suffix === '%' ? suffix : '');
                    }
                }, target);
            });
            statsObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

const heroStats = document.querySelector('.hero-stats');
if (heroStats) {
    statsObserver.observe(heroStats);
}

// Mobile menu toggle (optional - for future enhancement)
const createMobileMenu = () => {
    const nav = document.querySelector('. nav-content');
    const menuButton = document.createElement('button');
    menuButton.className = 'mobile-menu-button';
    menuButton.innerHTML = '☰';
    menuButton.style.display = 'none';
    menuButton.style. background = 'none';
    menuButton.style.border = 'none';
    menuButton.style.color = 'var(--text-primary)';
    menuButton.style.fontSize = '1.5rem';
    menuButton.style.cursor = 'pointer';
    
    // Show menu button on mobile
    const mediaQuery = window.matchMedia('(max-width: 768px)');
    const handleMobileMenu = (e) => {
        if (e.matches) {
            menuButton.style.display = 'block';
        } else {
            menuButton.style.display = 'none';
        }
    };
    
    mediaQuery.addListener(handleMobileMenu);
    handleMobileMenu(mediaQuery);
    
    nav.appendChild(menuButton);
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('AI Projects Portfolio loaded successfully');
    // createMobileMenu(); // Uncomment if you want mobile menu functionality
});

// Parallax effect for hero background
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const parallaxElements = document.querySelectorAll('.hero:: before, .hero::after');
    parallaxElements.forEach(el => {
        el.style.transform = `translateY(${scrolled * 0.5}px)`;
    });
});
