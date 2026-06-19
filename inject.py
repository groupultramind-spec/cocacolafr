import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove old pixels / trackers
html = re.sub(r'<script[^>]*src="js/OtAutoBlock\.js"[^>]*></script>', '', html)
html = re.sub(r'<script[^>]*src="js/otSDKStub\.js"[^>]*></script>', '', html)
html = re.sub(r'<script[^>]*src="js/_Incapsula_Resource\.js"[^>]*></script>', '', html)

# 2. Fix banner injection (remove previous if it exists)
html = re.sub(r'<!-- CUSTOM BANNER START -->.*?<!-- CUSTOM BANNER END -->', '', html, flags=re.DOTALL)

# Inject just BEFORE <div id="__next"> so React hydration doesn't touch it
banner_code = """
<!-- CUSTOM BANNER START -->
<style>
  .custom-banner-slider {
    position: relative;
    width: 100%;
    max-width: 1200px;
    margin: 20px auto;
    overflow: hidden;
    height: 400px;
    border-radius: 8px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  }
  .custom-banner-slider img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    position: absolute;
    top: 0;
    left: 100%;
    transition: left 0.5s ease-in-out;
  }
  .custom-banner-slider img.active {
    left: 0;
  }
  .custom-banner-slider img.prev {
    left: -100%;
  }
  .custom-slider-nav {
    position: absolute;
    bottom: 15px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 10px;
    z-index: 10;
  }
  .custom-slider-nav button {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    border: none;
    background: rgba(255, 255, 255, 0.5);
    cursor: pointer;
    padding: 0;
  }
  .custom-slider-nav button.active {
    background: rgba(255, 255, 255, 1);
  }
  @media (max-width: 768px) {
    .custom-banner-slider {
        height: 200px;
    }
  }
</style>
<div class="custom-banner-slider" id="customBannerSlider">
  <img src="/banners/image1.png" class="active" />
  <img src="/banners/imagem2.png" />
  <img src="/banners/imagem3.png" />
  <img src="/banners/imagem4.png" />
  <div class="custom-slider-nav" id="customSliderNav">
    <button class="active"></button>
    <button></button>
    <button></button>
    <button></button>
  </div>
</div>
<script>
  (function() {
    let current = 0;
    const slider = document.getElementById('customBannerSlider');
    if (!slider) return;
    const images = slider.querySelectorAll('img');
    const buttons = document.getElementById('customSliderNav').querySelectorAll('button');
    function show(index) {
      if (index === current) return;
      images[current].className = 'prev';
      buttons[current].classList.remove('active');
      current = index;
      images[current].className = 'active';
      buttons[current].classList.add('active');
      setTimeout(() => {
        for(let i=0; i<images.length; i++) {
          if (i !== current) images[i].className = '';
        }
      }, 500);
    }
    buttons.forEach((btn, idx) => {
      btn.addEventListener('click', () => show(idx));
    });
    setInterval(() => {
      show((current + 1) % images.length);
    }, 4000);
  })();
</script>
<!-- CUSTOM BANNER END -->
"""

target = '<div id="__next">'
if target in html:
    html = html.replace(target, banner_code + "\n" + target)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html successfully.")
