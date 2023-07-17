import styles from './sea_bird.module.css'
import { defineComponent, h, VNode} from 'vue'

export const SeaBirdMotion = defineComponent({
    name: 'SeaBirdMotion',
    methods: {
    },
    render() {
        const nodes = []
        for(let i=0; i<8; i++){
            nodes.push(h('div', {class: styles["birdposition"]},
                        h('div', {class: styles["bird"]}, [
                            h('div', {class:[styles["wing"], styles["-left"]]}),
                            h('div', {class:[styles["wing"], styles["-right"]]})
                        ])))
        }
        return h('div', {class:styles["sea_bird_scene"]}, nodes)
    }
})

export default SeaBirdMotion

