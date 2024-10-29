$(".banner-blur").removeClass("opacity-0");

setTimeout(() => {$(".banner-blur").addClass("animation-glow");}, 4000);

$(window).on('scroll', () => {
    $('body').css("--scrolly", window.scrollY);
})