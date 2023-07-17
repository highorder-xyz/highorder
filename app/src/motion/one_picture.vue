<script lang="ts">
import { defineComponent, reactive, h } from 'vue'

export default defineComponent({
    props: {
        url: { type: String, default: "" }
    },
    render() {
        return h('img', {class: "one_picture", src:this.$props.url})
    }
})

</script>

<style  scoped>
.one_picture {
    margin: 0;
    overflow: hidden;
    width: 100vw;
}
</style>