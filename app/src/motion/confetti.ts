
import confetti from 'canvas-confetti';

export function showConfetti(args: object) {
    const count = (args as {count: number}).count ?? 0
    const end = Date.now() + (count + 2) * 200;
    const colors = ['#008000', '#FFA500'];
    const motion_canvas = window.document.getElementById('motion_canvas') as HTMLCanvasElement
    const confetti_show = confetti.create(motion_canvas, {resize: true})

    function frame() {
        confetti_show({
            particleCount: 20,
            angle: 60,
            spread: 80,
            origin: { x: 0, y: 1 },
            colors: colors,
            shapes: ['square'],
            disableForReducedMotion: true,
        });
        confetti_show({
            particleCount: 20,
            angle: 120,
            spread: 80,
            origin: { x: 1, y: 1 },
            colors: colors,
            shapes: ['square'],
            disableForReducedMotion: true,
        });
    }

    function animationFrame() {
        setTimeout(() => {
            requestAnimationFrame(frame)
            if (Date.now() < end) {
                animationFrame();
            }
        }, 200);
    }
    animationFrame()

}