<script lang="ts">
import { defineComponent, reactive, h } from 'vue'

export default defineComponent({
    props: {
        grass_number: { type: Number, default: 100 }
    },
    methods: {
        buildGrass(index: number){
            var colors = ["green", "darkgreen", "olive"];
            const style = {
                width: Math.random() * 0.5 + 1.5 + "%",
                height: Math.random() * 30 + 50 + "%",
                backgroundColor: colors[Math.floor(Math.random() * colors.length)],
                animationDelay: Math.random() * 3 + "s",
                left: index + '%',
                zIndex: index % 2 === 0 ? -1 : 1
            }
            return h('div', {class:"grass", style:style})
        }
    },
    render() {
        const nodes = []
        for(let i=0; i<this.grass_number; i++){
            nodes.push(this.buildGrass(i))
        }
        return h('div', {class: "wall_footer"}, nodes)
    }
})

</script>

<style  scoped>
.grass {
	width: 1.5%;
	height: 80%;
	bottom: 0;
	background-color: green;
	background: linear-gradient(to bottom, forestgreen 75%, olive);
	background-size: 120% auto;
	box-shadow: 0 0 4px black;
	border-radius: 100% 100% 0 0;
	transform-origin: center bottom;
	pointer-events: none;
	animation: sway 5s linear infinite;
    position: absolute;
}
@keyframes sway {
	25% {
		transform: skewX(3deg);
	}
	75% {
		transform: skewX(-3deg);
	}
}

.wall_footer {
    background: linear-gradient(163deg, transparent 0px, transparent 1px, BlanchedAlmond 1px, BlanchedAlmond 14px, transparent 14px), linear-gradient(161deg, transparent 0px, #FFF 2px, BlanchedAlmond 2px, BlanchedAlmond 16px, transparent 16px), linear-gradient(343deg, transparent 0px, transparent 1px, #ffe1b4 1px, BlanchedAlmond 14px, transparent 14px), linear-gradient(343deg, transparent 0px, transparent 1px, #ffe1b4 1px, BlanchedAlmond 14px, transparent 14px);
    background-color: #FFF;
    background-size: 48px 30px;
    background-position: 2px 1px, 23px 16px, 48px 15px, 21px 30px;
    margin: 0;
    overflow: hidden;
    min-height: 80px;
    max-height: 120px;
    width: 100vw;
    max-width: 500px;
    position:relative;
}
</style>