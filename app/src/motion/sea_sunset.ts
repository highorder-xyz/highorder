import styles from './sea_sunset.module.css'
import { defineComponent, h, VNode} from 'vue'

export const SeaSunsetMotion = defineComponent({
    name: 'SeaSunsetMotion',
    methods: {
    },
    render() {
        return h('div', { "class": styles["sea_sunset"] }, [
            h('div', {class: styles["sun"]}),
            h('div', {class: styles["sea"]}, [
                h('div', {class: styles["wave"]}),
                h('div', {class: styles["wave"]}),
                h('div', {class: styles["wave"]}),
                h('div', {class: styles["wave"]}),
                h('div', {class: styles["wave"]}),
                h('div', {class: styles["wave"]})
            ])
        ])
    }
})

export default SeaSunsetMotion