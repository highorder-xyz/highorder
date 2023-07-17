<script lang="ts">
import { defineComponent, reactive, h } from 'vue'

export default defineComponent({
    props: {
        vines: { type: Number, default: 20 }
    },
    methods: {
        buildVine(){
            const num = Math.ceil(Math.random() * 10) * 5
            const style = {
                width: '3px',
                height: num*3 + 'px',
                background: 'hsl(10deg,50%,'+(Math.random() * 40 + 20)+'%)',
                top: 0,
                transform: 'translateY(-100%)',
                animationDelay: Math.random() * 3 + 's',
                animationDuration: num * .25 + 's',
                borderRadius: '0 0 1rem 1rem',
                pointerEvents: 'none',
            }
            const leaf_count = Math.floor(num*0.4)
            const leaf_nodes = []
            for(let i=0; i<leaf_count; i++){
                const side = Math.random() < .5 ? 'scaleX(-1)' : ''
                const show = Math.random() < .5 ? 'hidden' : ''
                const color = 'hsl(150deg,50%,'+(Math.random() * 40 + 20)+'%)'
                const leaf_style = {
                    background: `${color}`,
                    visibility: `${show}`,
                    transform: `${side}`
                }
                leaf_nodes.push(h('div', {class:"leaf_box", style: leaf_style}))
            }
            return h('div', {class:"flower", style:style}, leaf_nodes)
        }
    },
    render() {
        const nodes = []
        for(let i=0; i<this.vines; i++){
            nodes.push(this.buildVine())
        }
        return h('div', {class: "wall"}, nodes)
    }
})

</script>

<style  scoped>
.flower {
    filter: drop-shadow(4px 4px 2px rgba(0, 0, 0, .25));
    animation: grow 1s forwards;
    margin-right: 22px;
    margin-left: 2px;
}

@keyframes grow {
    100% {
        transform: translateY(0%);
    }
}

.leaf_box {
    width: 11px;
    height:7.8px;
    display:block;
    border-radius:0% 75% 0% 75%;
    transform-origin:1.5px 50%;
}

.wall {
    background: linear-gradient(163deg, transparent 0px, transparent 1px, BlanchedAlmond 1px, BlanchedAlmond 14px, transparent 14px), linear-gradient(161deg, transparent 0px, #FFF 2px, BlanchedAlmond 2px, BlanchedAlmond 16px, transparent 16px), linear-gradient(343deg, transparent 0px, transparent 1px, #ffe1b4 1px, BlanchedAlmond 14px, transparent 14px), linear-gradient(343deg, transparent 0px, transparent 1px, #ffe1b4 1px, BlanchedAlmond 14px, transparent 14px);
    background-color: #FFF;
    background-size: 48px 30px;
    background-position: 2px 1px, 23px 16px, 48px 15px, 21px 30px;
    margin: 0;
    overflow: hidden;
    display: flex;
    align-items: flex-start;
    min-height: 200px;
    max-height: 400px;
    width: 100vw;
    max-width: 500px;
}
</style>