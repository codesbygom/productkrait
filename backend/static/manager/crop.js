// Product photo cropper for the manager (Cropper.js, loaded from the CDN).
//
// Progressive enhancement of <input type="file" data-width data-height ...>:
// picking or dropping a photo opens a fixed-ratio crop box (pan = drag,
// zoom = wheel/pinch/buttons). On submit the input's file is swapped for the
// cropped image at exactly data-width x data-height, then the form is sent as
// usual. The server re-checks and normalises the file, so this is a
// convenience, not the only safeguard.
(function () {
    const input = document.querySelector('input[type=file][data-width]');
    if (!input || typeof Cropper === 'undefined') return;

    const form = input.closest('form');
    const width = parseInt(input.dataset.width, 10);
    const height = parseInt(input.dataset.height, 10);
    const minW = parseInt(input.dataset.minWidth, 10) || 0;
    const minH = parseInt(input.dataset.minHeight, 10) || 0;

    const zone = document.getElementById('crop-zone');
    const drop = document.getElementById('crop-drop');
    const stage = document.getElementById('crop-stage');
    const img = document.getElementById('crop-preview');
    const tools = document.getElementById('crop-tools');
    const note = document.getElementById('crop-note');

    input.hidden = true;
    input.required = false;   // a hidden required input blocks submit silently; the server still requires it
    zone.hidden = false;

    let cropper = null;
    let cropped = false;

    function say(text, isError) {
        note.textContent = text || '';
        note.classList.toggle('is-error', !!isError);
    }

    function load(file) {
        if (!file) return;
        if (!file.type.startsWith('image/')) {
            say('Please choose an image file.', true);
            return;
        }
        cropper?.destroy();
        cropped = false;
        const url = URL.createObjectURL(file);
        const probe = new Image();
        probe.onload = function () {
            if (probe.naturalWidth < minW || probe.naturalHeight < minH) {
                say('Image is too small (' + probe.naturalWidth + 'x' + probe.naturalHeight + '). Minimum is ' + minW + 'x' + minH + '.', true);
                URL.revokeObjectURL(url);
                return;
            }
            say('Drag to move, scroll or use the buttons to zoom. Output: ' + width + 'x' + height + '.');
            stage.hidden = false;
            tools.hidden = false;
            img.src = url;
            cropper = new Cropper(img, {
                aspectRatio: width / height,
                viewMode: 1,
                dragMode: 'move',
                autoCropArea: 1,
                background: false,
                responsive: true,
            });
        };
        probe.src = url;
    }

    input.addEventListener('change', () => load(input.files[0]));
    document.getElementById('crop-browse').addEventListener('click', () => input.click());

    ['dragenter', 'dragover'].forEach((ev) => drop.addEventListener(ev, (e) => {
        e.preventDefault();
        drop.classList.add('dragover');
    }));
    ['dragleave', 'drop'].forEach((ev) => drop.addEventListener(ev, (e) => {
        e.preventDefault();
        drop.classList.remove('dragover');
    }));
    drop.addEventListener('drop', (e) => load(e.dataTransfer.files[0]));

    tools.querySelectorAll('[data-zoom]').forEach((btn) => {
        btn.addEventListener('click', () => cropper?.zoom(parseFloat(btn.dataset.zoom)));
    });
    tools.querySelector('[data-reset]').addEventListener('click', () => cropper?.reset());

    form.addEventListener('submit', function (e) {
        if (!cropper || cropped) return;   // nothing new picked, or already swapped
        e.preventDefault();
        const canvas = cropper.getCroppedCanvas({
            width: width,
            height: height,
            imageSmoothingQuality: 'high',
            fillColor: '#fff',
        });
        canvas.toBlob(function (blob) {
            if (!blob) { say('Could not process the image.', true); return; }
            const dt = new DataTransfer();
            dt.items.add(new File([blob], 'product.jpg', { type: 'image/jpeg' }));
            input.files = dt.files;
            cropped = true;
            form.requestSubmit ? form.requestSubmit() : form.submit();
        }, 'image/jpeg', 0.92);
    });
})();
