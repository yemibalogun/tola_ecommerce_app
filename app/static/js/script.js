(function($) {

    "use strict";

    var searchPopup = function() {

        $('#header-nav').on('click', '.search-button', function() {
            $('.search-popup').toggleClass('is-visible');
        });

        $('#header-nav').on('click', '.btn-close-search', function() {
            $('.search-popup').toggleClass('is-visible');
        });

        $(".search-popup-trigger").on("click", function(e) {
            e.preventDefault();
            $(".search-popup").addClass("is-visible");

            setTimeout(function() {
                $("#search-popup").focus();
            }, 350);
        });

        $(".search-popup").on("click", function(e) {
            if (
                $(e.target).is(".search-popup-close") ||
                $(e.target).is(".search-popup-close svg") ||
                $(e.target).is(".search-popup-close path") ||
                $(e.target).is(".search-popup")
            ) {
                e.preventDefault();
                $(this).removeClass("is-visible");
            }
        });

        $(document).keyup(function(e) {
            if (e.which === 27) {
                $(".search-popup").removeClass("is-visible");
            }
        });
    };


    var initProductQty = function() {

        $('.product-qty').each(function() {

            var $el_product = $(this);

            $el_product.find('.quantity-right-plus').click(function(e) {
                e.preventDefault();

                var quantity = parseInt($el_product.find('#quantity').val()) || 0;
                $el_product.find('#quantity').val(quantity + 1);
            });

            $el_product.find('.quantity-left-minus').click(function(e) {
                e.preventDefault();

                var quantity = parseInt($el_product.find('#quantity').val()) || 0;

                if (quantity > 0) {
                    $el_product.find('#quantity').val(quantity - 1);
                }
            });

        });
    };


    $(document).ready(function() {

        searchPopup();
        initProductQty();

        /* ==============================
           PRODUCT SWIPERS
        ============================== */

        new Swiper(".product-swiper", {
            slidesPerView: 4,
            spaceBetween: 10,
            pagination: {
                el: "#mobile-products .swiper-pagination",
                clickable: true,
            },
            breakpoints: {
                0: { slidesPerView: 2, spaceBetween: 20 },
                980: { slidesPerView: 4, spaceBetween: 20 }
            },
        });

        new Swiper(".product-watch-swiper", {
            slidesPerView: 4,
            spaceBetween: 10,
            pagination: {
                el: "#smart-watches .swiper-pagination",
                clickable: true,
            },
            breakpoints: {
                0: { slidesPerView: 2, spaceBetween: 20 },
                980: { slidesPerView: 4, spaceBetween: 20 }
            },
        });

        new Swiper(".testimonial-swiper", {
            slidesPerView: 1,
            spaceBetween: 30,
            centeredSlides: true,
            loop: true,
            autoplay: {
                delay: 4000,
                disableOnInteraction: false,
            },
            speed: 800,
            navigation: {
                nextEl: ".swiper-arrow-next",
                prevEl: ".swiper-arrow-prev",
            },
            pagination: {
                el: ".swiper-pagination",
                clickable: true,
            }
        });


        /* ==============================
           HERO BACKGROUND HANDLER
        ============================== */

        const slides = document.querySelectorAll(".banner-slide");

        slides.forEach(slide => {
            const bgImage = slide.dataset.bgImage;
            const bgColor = slide.dataset.bgColor;

            if (bgImage) {
                slide.style.setProperty("--banner-bg-image", `url(${bgImage})`);
            } else if (bgColor) {
                slide.style.setProperty("--banner-bg-color", bgColor);
            }
        });

    });

})(jQuery);
(function($) {

    "use strict";

    var searchPopup = function() {

        $('#header-nav').on('click', '.search-button', function() {
            $('.search-popup').toggleClass('is-visible');
        });

        $('#header-nav').on('click', '.btn-close-search', function() {
            $('.search-popup').toggleClass('is-visible');
        });

        $(".search-popup-trigger").on("click", function(e) {
            e.preventDefault();
            $(".search-popup").addClass("is-visible");

            setTimeout(function() {
                $("#search-popup").focus();
            }, 350);
        });

        $(".search-popup").on("click", function(e) {
            if (
                $(e.target).is(".search-popup-close") ||
                $(e.target).is(".search-popup-close svg") ||
                $(e.target).is(".search-popup-close path") ||
                $(e.target).is(".search-popup")
            ) {
                e.preventDefault();
                $(this).removeClass("is-visible");
            }
        });

        $(document).keyup(function(e) {
            if (e.which === 27) {
                $(".search-popup").removeClass("is-visible");
            }
        });
    };


    var initProductQty = function() {

        $('.product-qty').each(function() {

            var $el_product = $(this);

            $el_product.find('.quantity-right-plus').click(function(e) {
                e.preventDefault();

                var quantity = parseInt($el_product.find('#quantity').val()) || 0;
                $el_product.find('#quantity').val(quantity + 1);
            });

            $el_product.find('.quantity-left-minus').click(function(e) {
                e.preventDefault();

                var quantity = parseInt($el_product.find('#quantity').val()) || 0;

                if (quantity > 0) {
                    $el_product.find('#quantity').val(quantity - 1);
                }
            });

        });
    };


    $(document).ready(function() {

        searchPopup();
        initProductQty();

        /* ==============================
           PRODUCT SWIPERS
        ============================== */

        new Swiper(".product-swiper", {
            slidesPerView: 4,
            spaceBetween: 10,
            pagination: {
                el: "#mobile-products .swiper-pagination",
                clickable: true,
            },
            breakpoints: {
                0: { slidesPerView: 2, spaceBetween: 20 },
                980: { slidesPerView: 4, spaceBetween: 20 }
            },
        });

        new Swiper(".product-watch-swiper", {
            slidesPerView: 4,
            spaceBetween: 10,
            pagination: {
                el: "#smart-watches .swiper-pagination",
                clickable: true,
            },
            breakpoints: {
                0: { slidesPerView: 2, spaceBetween: 20 },
                980: { slidesPerView: 4, spaceBetween: 20 }
            },
        });

        new Swiper(".testimonial-swiper", {
            slidesPerView: 1,
            spaceBetween: 30,
            centeredSlides: true,
            loop: true,
            autoplay: {
                delay: 4000,
                disableOnInteraction: false,
            },
            speed: 800,
            navigation: {
                nextEl: ".swiper-arrow-next",
                prevEl: ".swiper-arrow-prev",
            },
            pagination: {
                el: ".swiper-pagination",
                clickable: true,
            }
        });


        /* ==============================
           HERO BACKGROUND HANDLER
        ============================== */

        const slides = document.querySelectorAll(".banner-slide");

        slides.forEach(slide => {
            const bgImage = slide.dataset.bgImage;
            const bgColor = slide.dataset.bgColor;

            if (bgImage) {
                slide.style.setProperty("--banner-bg-image", `url(${bgImage})`);
            } else if (bgColor) {
                slide.style.setProperty("--banner-bg-color", bgColor);
            }
        });

    });

})(jQuery);
