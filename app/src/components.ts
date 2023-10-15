
import { defineComponent, ComponentInternalInstance, h, VNode, PropType, DefineComponent, renderSlot, withModifiers } from 'vue';
import gsap from 'gsap'
import styles from './components.module.css'
import 'animate.css';
import { Swiper, SwiperSlide } from "swiper/vue";
import "swiper/css";
import "swiper/css/effect-cards";
import { EffectCards } from "swiper";
import { VideoPlayer as VideoJSVideoPlayer } from '@videojs-player/vue';
import 'video.js/dist/video-js.css'
import { RichTextCompiler, RichTextPart, RichTextTag } from './common/richtext';
import PrimeButton from 'primevue/button';
import PrimeCard from 'primevue/card';
import PrimeInputText from 'primevue/inputtext';
import PrimePassword from 'primevue/password';
import { PrimeIcons } from 'primevue/api';


gsap.ticker.fps(10);

function randomString(n: number, charset?: string): string {
    let res = '';
    let chars =
        charset || 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let charLen = chars.length;

    for (var i = 0; i < n; i++) {
        res += chars.charAt(Math.floor(Math.random() * charLen));
    }

    return res;
}


const icon_components: Record<string, string> = {
}

export function init_components() {
    for (let [key, value] of Object.entries(PrimeIcons)) {
        const new_key = key.toLowerCase().replaceAll('_', '-')
        icon_components[new_key] = value
    }
}


export function get_size_name(size: number) {
    const names = ['extra_extra_large', 'extra_large', 'large', 'normal', 'medium', 'small', 'extra_small']
    if (size < 0) {
        size = 0
    }
    if (size > 6) {
        size = 6
    }
    return names[size]
}

export function get_size_ratio(size: number) {
    const sizeRatio: Record<number, number> = {
        0: 1.95,
        1: 1.56,
        2: 1.25,
        3: 1,
        4: 0.8,
        5: 0.64,
        6: 0.51
    }
    let text_size = size
    if (size > 6) {
        text_size = 6
    }
    if (size < 0) {
        text_size = 0
    }
    if (sizeRatio.hasOwnProperty(text_size))
        return sizeRatio[text_size]
    return 1
}


export function get_text_color(name: string) {
    const colorMapping: Record<string, string> = {
        "text": "yellow",
        "text2": "orange",
        "text3": "red",
        "primary": "green",
        "primarytext": "white",
        "secondary": "#cccccc",
        "secondarytext": "black"
    }
    if (colorMapping.hasOwnProperty(name)) {
        return colorMapping[name]
    }
    return ""
}

const icon_assets: Record<string, string> = {
    "wx_login": "assets/common/wx_login.png",
    "wx_logo": "assets/common/wx_logo.png",
    "wx_moments": "assets/common/wx_moments.png"
}

export const Button = defineComponent({
    name: 'Button',
    props: {
        icon: { type: String },
        text: { type: String, default: "" },
        href: { type: String, default: ""},
        open_new: { type: Boolean, default: false},
        sub_text: { type: String, default: "" },
        style: { type: Object, default: {}},
        disable: { type: Boolean, default: false},
        disable_text: { type:String, default: ""},
        height: { type: Number },
        size_hint: {type: Boolean, default: true},
        h_size: { type: Number, default: 3 },
        v_size: { type: Number, default: 3 },
        text_size: { type: Number, default: 3 },
        icon_size: { type: Number, default: 3 },
        icon_pos: { type: String, default: "left" },
        v_padding: { type: Number },
        h_padding: { type: Number },
        v_margin: { type: Number, default: 3 },
        h_margin: { type: Number, default: 3 },
        color: { type: String, default: "surface" }
    },
    computed: {
        iconSize(): Number {
            const sizeRatio: Record<number, number> = {
                3: 1,
                2: 1.5,
                1: 2.25,
                4: 0.75,
                5: 0.5,
            }
            let text_size = this.text_size
            if (this.text_size > 5) {
                text_size = 5
            }
            if (this.text_size < 1) {
                text_size = 1
            }
            return 24 * sizeRatio[text_size]
        }
    },
    emits: {
        clicked: null
    },
    methods: {
        renderIcon(): VNode | undefined {
            const icon = this.$props.icon
            if (icon) {
                if (icon in icon_assets) {
                    const asset_url = icon_assets[icon]
                    return h('img', { style: { "max-height": `${this.iconSize}px`, "max-width": "100%" }, src: asset_url })
                } else {
                    return h('img', { width: this.iconSize, height: this.iconSize, src: icon })
                }
            }

        },

        renderInner() {
            const textClasses = [styles["button-text"]]
            const sizeName = get_size_name(this.$props.text_size)
            textClasses.push(styles[sizeName])
            if (this.$props.text) {
                return h('div', { "class": textClasses }, h(RichText, { text: this.$props.text}))
            } else if(this.$slots.default !== undefined) {
                return renderSlot(this.$slots, "default", {})
            }
        },

        renderSubText() {
            const textClasses = [styles["button-text"]]
            const sizeName = get_size_name(this.$props.text_size + 2)
            textClasses.push(styles[sizeName])
            // const nodes = []
            // for(const text of this.$props.sub_text.split('\n')){
            //     nodes.push(h('div', text))
            // }
            const sub_text = this.disable === true ? this.disable_text : this.sub_text
            if (sub_text.length > 0) {
                return h('div', { "class": textClasses }, h(RichText, { text: sub_text, style: { "text-align": "center" } }))
            } else {
                return h('div', { "class": textClasses })
            }

        },

        renderChildren() {
            const children: (VNode | undefined)[] = []
            let row_children: (VNode | undefined)[] = []
            if (this.$props.icon) {
                if (!(this.$props.icon in icon_components) && (this.icon_pos === 'left' || this.icon_pos === 'top')){
                    row_children.push(this.renderIcon())
                }
            }
            if (this.$props.text) {
                row_children.push(this.renderInner())
            }

            if (this.$props.icon) {
                if (this.icon_pos === 'right' || this.icon_pos === 'bottom') {
                    row_children.push(this.renderIcon())
                }

            }

            children.push(h('div', { class: [styles["text-row"]] }, row_children))

            if (this.$props.sub_text) {
                row_children = []
                row_children.push(this.renderSubText())
                children.push(h('div', { class: [styles["text-row"]] }, row_children))
            }
            return children
        }
    },
    render() {
        const btnClasses = []
        let icon = ''
        if (["top", "bottom"].includes(this.icon_pos)) {
            btnClasses.push(styles["content_column"])
        }

        const styleTags:Record<string, any> = {}
        const tags = this.style.tags ?? []

        for(const tag of tags){
            if(tag === 'text'){
                styleTags['text'] = true
            } else if(["primary", "secondary"].includes(tag)){
                styleTags['severity'] = tag
            }
        }
        const btnStyle: Record<string, any> = {}
        if (this.$props.color === 'primary') {
            btnClasses.push(styles['primary'])
        }

        if(this.size_hint){
            const vSizeName = get_size_name(this.$props.v_size)
            btnClasses.push(styles[`v_${vSizeName}`])
            const hSizeName = get_size_name(this.$props.h_size)
            btnClasses.push(styles[`h_${hSizeName}`])
        }

        if (this.$props.icon && this.$props.icon in icon_components) {
            icon = icon_components[this.$props.icon]
        } else {
            icon = this.$props.icon ? `pi pi-${this.$props.icon}`: "pi"
        }

        const btn = h(PrimeButton, {
                label: this.text,
                icon: icon,
                "class": btnClasses,
                style: btnStyle,
                disabled: this.disable,
                ...styleTags,
                onClick: (evt: any) => { evt.stopPropagation(); this.$emit("clicked") }
            },
            {
                // "default": () => {
                //     return this.renderChildren()
                // }
            }
        )
        if(this.href.length > 0){
            return h('a', {href: this.href, "target": this.open_new === true ? '_blank' : '_self'}, btn)
        } else {
            return btn;
        }
    }
});

export const Link = defineComponent({
    name: 'Link',
    props: {
        text: { type: String, default: "" },
        open_mode: { type: String, default: "new" },
        target_url: { type: String, default: ""}
    },
    emits: {
        clicked: null
    },
    render() {
        return h(PrimeButton, {
            label: this.text,
            link: true,
            onClick: (evt: any) => { evt.stopPropagation(); this.$emit("clicked", this.target_url, this.open_mode) }
        })
    }
});

export const IconButton = defineComponent({
    name: 'IconButton',
    props: {
        icon: { type: String, default: "", required: true },
        size: { type: Number, default: 24 }
    },
    emits: {
        clicked: null
    },
    methods: {
        renderIcon(): VNode {
            return h('img', { width: this.size, height: this.size, src: this.$props.icon })
        }

    },
    render() {
        let icon = ''
        const sub_nodes = []
        if (this.$props.icon in icon_components){
            icon = icon_components[this.$props.icon]
        } else {
            sub_nodes.push(this.renderIcon())
        }
        return h(PrimeButton, {
                icon: icon, "class": styles["icon-button"],
                onClick: (evt: any) => { evt.stopPropagation(); this.$emit("clicked") }
            },
            {
                "default": () => {
                    if(!(this.$props.icon in icon_components)){
                        return this.renderIcon()
                    }
                }
            }
        )
    }
});

export const IconNumberButton = defineComponent({
    name: 'IconNumberButton',
    props: {
        number: { type: Number, default: 0 },
        maxDigits: { type: Number, default: 2 },
        size: { type: Number, default: 24 },
        icon: { type: String, default: "", required: true },
        minClickDuration: { type: Number, default: 500 }
    },
    data() {
        return {
            'lastClickTime': 0
        }
    },
    emits: {
        clicked: null
    },
    computed: {
        numberText(): string {
            const maxNumber = 10 ** this.maxDigits - 1;
            if (this.$props.number < 0) {
                return '0'
            } else if (this.$props.number <= maxNumber) {
                return this.$props.number.toString()
            } else {
                return maxNumber.toString() + '+'
            }
        }
    },

    methods: {
        tryEmit(): void {
            const now_ts = new Date().getTime()
            if (now_ts - this.lastClickTime > this.$props.minClickDuration) {
                this.$emit("clicked")
                this.lastClickTime = now_ts
            }
        },
        renderIcon(): VNode {
            const icon = this.$props.icon
            if (icon in icon_components) {
                return h('div', { width: this.size, height: this.size, class:icon_components[icon]})
            } else {
                return h('img', { width: this.size, height: this.size, src: icon })
            }
        }
    },

    render() {
        return h('button', {
            "type": "button",
            "class": styles["icon-number-button"],
            "data-badge": this.numberText,
            onClick: (evt: any) => { evt.stopPropagation(); this.tryEmit() }
        }, [
            this.renderIcon(),
        ])
    }
});

export const IconNumberText = defineComponent({
    name: 'IconNumberText',
    props: {
        number: { type: Number, required: true },
        maxDigits: { type: Number, default: 6 },
        icon: { type: String, default: "", required: true },
    },
    data() {
        return {
            'iconBounceClass': ""
        }
    },
    computed: {
        numberText(): string {
            const maxNumber = 10 ** this.maxDigits - 1;
            if (this.$props.number <= maxNumber) {
                return this.$props.number.toString()
            } else {
                return maxNumber.toString() + '+'
            }
        }
    },
    watch: {
        number(oldValue, newValue) {
            this.$data.iconBounceClass = styles["bounce"]
        }
    },
    methods: {
        renderIcon(): VNode {
            const icon = this.$props.icon
            if (icon in icon_components) {
                return h('div', {
                    ref: "icon", width: 24, height: 24,
                    'number-text': this.numberText,
                    class: [this.iconBounceClass, icon_components[icon]],
                    onanimationend: () => {
                        this.$data.iconBounceClass = ''
                    }
                })
            } else {
                return h('img', {
                    ref: "icon", width: 24, height: 24, src: icon,
                    'number-text': this.numberText,
                    class: [this.iconBounceClass],
                    onanimationend: () => {
                        this.$data.iconBounceClass = ''
                    }
                })
            }
            return h('div')
        },

        renderNumberText(): VNode {
            return h('div', {}, this.numberText)
        }
    },

    render() {
        return h('div', { class: styles["icon-number-text"] }, [
            this.renderIcon(),
            this.renderNumberText()
        ])
    }
});

export const Divider = defineComponent({
    name: 'Divider',
    props: {
        widthHint: { type: Number, default: 100 }
    },
    methods: {
    },
    render() {
        return h('div', { "class": styles["divider"], style: { width: `${this.widthHint}%` } })
    }
});

export const Title = defineComponent({
    name: 'Title',
    props: {
        title: { type: String, required: true },
        level: { type: Number, default: 1 },
        sub_title: { type: String, default: ""}
    },
    methods: {
    },
    render() {
        const nodes: VNode[] = []
        nodes.push(h('span', { "class": styles[`title-${this.level}`] }, this.title))
        if(this.sub_title.length > 0){
            nodes.push(h('span', { "class": styles[`title-sub-${this.level}`] }, this.sub_title))
        }
        return h('div', { "class": styles['title'] }, nodes)
    }
});


export const Paragraph = defineComponent({
    name: 'Paragraph',
    props: {
        text: { type: String, required: true },
        align: { type: String, default: "start" },
        isRich: { type: Boolean, default: true }
    },
    render() {
        const style: any = {}
        let align = this.align
        if(align === 'start'){
            align = 'left'
        } else if (align === 'end') {
            align = 'right'
        }
        style["text-align"] = align
        if (this.isRich) {
            return h(RichText, { "class": styles["paragraph"], style: style, text: this.text })
        } else {
            const texts = this.text.split('\n')
            const nodes = [];
            for (const text of texts) {
                nodes.push(h('div', text))
            }
            return h('div', { "class": styles["paragraph"], style: style }, nodes)
        }

    }
});


export const BulletedList = defineComponent({
    name: 'BulletedList',
    props: {
        texts: { type: Array as PropType<Array<string>>, default: [] }
    },
    methods: {
    },
    render() {
        const children: VNode[] = []
        for (const text of this.texts) {
            children.push(h('li', {}, text))
        }
        return h('div', { "class": styles["bulleted-list"] }, h('ul', {}, children))
    }
});



export interface ActionDefinition {
    icon?: string,
    text?: string,
    size?: string,
    clicked?: () => void
}

export const Modal = defineComponent({
    name: 'Modal',
    props: {
        closeIcon: { type: Boolean, default: false },
        showNow: { type: Boolean, default: false, required: false },
        modal_id: { type: String, default: ""},
        title: { type: String, default: "" },
        title_action: { type: Object, default: undefined},
        text: { type: String, default: "" },
        text_size: { type: Number, default: 3 },
        animate: { type: Boolean, default: false },
        content_html: { type: String, default: "" },
        element_align: { type: String, default: "center"},
        element_justify: { type: String, default: "center"},
        actions: { type: Array as PropType<Array<ActionDefinition>>, default: () => ([]) },
        actionsVertical: { type: Boolean, default: false },
        actionsPosition: { type: String, default: "center" },
        actionConfirmText: { type: String, default: "" },
        actionCancelLink: { type: Boolean, default: false },
        actionCancelText: { type: String, default: "" }
    },
    computed: {
        actionConfirm(): boolean {
            return this.$props.actionConfirmText !== undefined && this.$props.actionConfirmText.length > 0
        },

        actionCancel(): boolean {
            return this.$props.actionCancelText !== undefined && this.$props.actionCancelText.length > 0
        }
    },
    data() {
        return {
            showModal: this.$props.showNow,
            textShowed: 0
        }
    },
    beforeMount() {
        this.showModal = this.$props.showNow;
    },
    created() {
        const textLength = this.text.length
        this.textShowed = 0
        if (this.animate) {
            gsap.to(this, {
                duration: 0.1 * textLength,
                ease: "none",
                overwrite: true,
                textShowed: Number(textLength) || 0,
            })
        } else {
            this.textShowed = textLength
        }
    },
    watch: {
        text(newText, oldText) {
            const textLength = newText.length
            this.textShowed = 0
            if (this.animate) {
                gsap.to(this, {
                    duration: 0.1 * textLength,
                    ease: "none",
                    overwrite: true,
                    textShowed: Number(textLength) || 0,
                })
            } else {
                this.textShowed = textLength
            }
        },
        modal_id(oldValue, newValue){
            this.showModal = this.$props.showNow
        }

    },
    emits: {
        modalClosed: null,
        modalConfirmed: null,
        modalCancelled: null,
        modalClicked: null,
        actionClicked: (name: string) => { return true }
    },
    methods: {
        show() {
            this.$data.showModal = true
        },

        hide() {
            this.$data.showModal = false
            this.$emit("modalClosed")
        },

        renderButtons() {
            const buttons: VNode[] = []
            for (const action of this.$props.actions) {
                buttons.push(h(Button, {
                    text: action.text ?? "", icon: action.icon ?? "", onClicked: () => {
                        if (action.clicked) {
                            action.clicked()
                        }
                        // this.$emit("actionClicked", action.name);
                    }
                }))
            }

            if (this.actionConfirm) {
                buttons.push(h(Button, {
                    color: 'primary',
                    text: this.$props.actionConfirmText, onClicked: () => {
                        this.$emit("modalConfirmed");
                        this.$data.showModal = false
                        this.$emit("modalClosed")
                    }
                }))
            }
            if (this.actionCancel) {
                buttons.push(h(Button, {
                    text: this.$props.actionCancelText, onClicked: () => {
                        this.$emit("modalCancelled");
                        this.$data.showModal = false
                        this.$emit("modalClosed")
                    }
                }))
            }

            if (!this.actionConfirm && !this.actionCancel){
                buttons.push(h('div', {
                    class: styles["close-bar"],
                    onClick: () => {
                        this.$emit("modalCancelled");
                        this.$data.showModal = false
                        this.$emit("modalClosed")
                    }
                }, "点击这里关闭"))
            }
            return buttons
        },
        renderElements() {
            const elements: VNode[] = []
            let title_action  = this.title_action
            if(this.title_action !== undefined && Object.keys(this.title_action).length == 0){
                title_action = undefined
            }
            if (this.title.length > 0 || title_action ) {
                const title_nodes: VNode[] = []

                if(title_action !== undefined){
                    title_nodes.push(
                        h('div', {"class": styles["title-action"]}, h(Button, {
                            text: title_action.text ?? "", icon: title_action.icon ?? "", "size_hint": false, onClicked: () => {
                                if (title_action && title_action.clicked) {
                                    title_action.clicked()
                                }
                            }})
                        )
                    )
                }
                title_nodes.push(h('div', {"class": styles["title"]}, h('b', this.title)))

                elements.push(h('div', { "class": styles["title-bar"] }, title_nodes))
            } else {
                elements.push(h('div'))
            }

            const lines: VNode[] = []
            if (this.text) {
                const parts = this.text.slice(0, this.textShowed).split('\n')
                for (const line of parts) {
                    if (line.length > 0)
                        lines.push(h('p', line))
                }
            }

            const textClasses = [styles["text"]]
            if (this.text_size <= 1) {
                textClasses.push(styles["extra_large"])
            } else if (this.text_size == 2) {
                textClasses.push(styles["large"])
            } else if (this.text_size == 4) {
                textClasses.push(styles["medium"])
            } else if (this.text_size >= 5) {
                textClasses.push(styles["small"])
            }

            if (lines.length > 0) {
                elements.push(h('div', { "class": textClasses }, lines))
            }

            if (this.$slots['default']) {
                const rendered = renderSlot(this.$slots, "default", {})
                const element_style = {
                    "justify-content": this.element_justify,
                    "align-items": this.element_align
                }
                elements.push(h('div', { "class": styles["custom_text"], "style": element_style }, rendered))
            }


            if (this.$props.content_html.length > 0) {
                elements.push(h('div', { "class": [styles["text"], styles["left"]], innerHTML: this.content_html }))
            }
            elements.push(h('div', {
                "class": [
                    styles[this.actionsVertical ? "vertical-options" : "options"],
                    styles[this.$props.actionsPosition]]
            }, [...this.renderButtons()]))

            return elements;
        }
    },
    render() {
        const modalClasses = [styles["modal"]]
        if (this.$data.showModal) {
            modalClasses.push(styles["appear"])
            return h('div', {
                "class": modalClasses,
                onPointerdown: (evt: any) => { evt.stopPropagation(); evt.stopImmediatePropagation(); },
                onMousedown: (evt: any) => { evt.stopPropagation(); evt.stopImmediatePropagation(); },
                onTouchstart: (evt: any) => { evt.stopPropagation(); evt.stopImmediatePropagation(); },
            }, [
                h('div', { "class": styles["content"] }, [
                    ...this.renderElements()
                ])
            ])
        }
    }

});

export type ModalType = InstanceType<typeof Modal>

export const NavBar = defineComponent({
    name: 'NavBar',
    props: {
        title: { type: String, default: "" },
        showHome: { type: Boolean, default: false },
        showBack: { type: Boolean, default: false },
        showPerson: { type: Boolean, default: false }
    },
    emits: {
        homeClicked: null,
        backClicked: null,
        personClicked: null
    },
    methods: {
        renderLeft(): VNode[] {
            const items: VNode[] = []
            if (this.$props.showHome) {
                items.push(h(IconButton, { 'icon': 'home', onClicked: () => { this.$emit('homeClicked') } }))
            } else if (this.$props.showBack) {
                items.push(h(IconButton, { 'icon': 'back', onClicked: () => { this.$emit('backClicked') } }))
            }
            return items
        },
        renderCenter(): VNode[] {
            const items: VNode[] = []
            items.push(h('div', { "class": styles["nav-title"] }, this.$props.title))
            return items
        },
        renderRight(): VNode[] {
            const items: VNode[] = []
            items.push(renderSlot(this.$slots, "default", {}))

            if (this.$props.showPerson) {
                items.push(h(IconButton, {
                    'icon': 'person',
                    onClicked: () => { this.$emit('personClicked') }
                }))
            }
            return items
        }
    },
    render() {
        return [
            h('div', { "class": styles["nav-bar"] }, [
                h('div', { "class": styles["nav-area-left"] }, this.renderLeft()),
                h('div', { "class": styles["nav-area-center"] }, this.renderCenter()),
                h('div', { "class": styles["nav-area-right"] }, this.renderRight()),
            ]),
            h('div', {"class": styles["nav-bar-placeholder"]})
        ]
    }
})

export type NavBarType = InstanceType<typeof NavBar>


export interface IconActionDefinition {
    name: string,
    text?: string,
    icon?: string,
    image?: string,
    count?: number,
    clicked?: Function
}

export const Header = defineComponent({
    name: 'Header',
    methods: {
    },
    render() {
        const items: VNode[] = []
        return [
            h('div', { "class": [styles["header"], styles['h-header']] }, [
                h('div', { "class": styles["header-start"] }, renderSlot(this.$slots, "start", {})),
                h('div', { "class": styles["header-center"] }, renderSlot(this.$slots, "center", {})),
                h('div', { "class": styles["header-end"] }, renderSlot(this.$slots, "end", {})),
            ]),
            h('div', {class: styles["h-header-holder"]})
        ]
    }
})

export const Footer = defineComponent({
    name: 'Footer',
    props: {
        text: { type: String, default: "" },
        leftActions: { type: Array as PropType<Array<ActionDefinition>>, default: () => { return [] } },
        rightActions: { type: Array as PropType<Array<ActionDefinition>>, default: () => { return [] } }
    },
    methods: {
        renderAction(act: ActionDefinition): VNode {
            if (act.icon) {
                return h(IconButton, { icon: act.icon, onClicked: () => { if (act.clicked) { act.clicked() } } })
            } else {
                return h(Button, { text: act.text, onClicked: () => { if (act.clicked) { act.clicked() } } })
            }
        },
        renderLeft(): VNode[] {
            const items: VNode[] = []
            return items
        },
        renderCenter(): VNode[] {
            const items: VNode[] = []
            items.push(h('div', { "class": styles["footer-text"] }, this.$props.text))
            return items
        },
        renderRight(): VNode[] {
            const items: VNode[] = []
            items.push(renderSlot(this.$slots, "default", {}))
            for (const act of this.rightActions) {
                items.push(this.renderAction(act))
            }
            return items
        }
    },
    render() {
        return h('div', { "class": [styles["footer"], styles["h-footer"]]}, [
            h('div', { "class": styles["footer-area-left"] }, this.renderLeft()),
            h('div', { "class": styles["footer-area-center"] }, this.renderCenter()),
            h('div', { "class": styles["footer-area-right"] }, this.renderRight()),
        ])
    }
})

export type FooterType = InstanceType<typeof Footer>

export const ActionBar = defineComponent({
    name: 'ActionBar',
    props: {
        actions: { type: Array as PropType<Array<IconActionDefinition>>, default: () => { return [] } },
        leftActions: { type: Array as PropType<Array<IconActionDefinition>>, default: () => { return [] } },
        rightActions: { type: Array as PropType<Array<IconActionDefinition>>, default: () => { return [] } }
    },
    emits: {
        actionTriggered: (name: string) => { return true },
    },
    methods: {
        renderActions(actions: Array<IconActionDefinition>) {
            const items: VNode[] = []
            for (const action of actions) {
                if (action.count !== undefined) {
                    items.push(h(IconNumberButton, {
                        name: action.name,
                        icon: action.icon,
                        number: action.count,
                        size: 28,
                        onClicked: () => {
                            if (action.clicked) {
                                action.clicked()
                            }
                            this.$emit('actionTriggered', action.name)
                        }
                    }))
                } else if (action.text !== undefined) {
                    items.push(h(Button, {
                        name: action.name,
                        text: action.text,
                        style: { "height": "36px" },
                        h_size: 5,
                        onClicked: () => {
                            if (action.clicked) {
                                action.clicked()
                            }
                            this.$emit('actionTriggered', action.name)
                        }
                    }))
                } else {
                    items.push(h(IconButton, {
                        name: action.name,
                        icon: action.icon,
                        size: 28,
                        onClicked: () => {
                            if (action.clicked) {
                                action.clicked()
                            }
                            this.$emit('actionTriggered', action.name)
                        }
                    }))
                }

            }
            return items
        },
    },
    render() {
        return h('div', { "class": styles["actionbar"] }, [
            h('div', { "class": styles["actionbar-left"] }, this.renderActions(this.$props.leftActions)),
            h('div', { "class": styles["actionbar-center"] }, this.renderActions(this.$props.actions)),
            h('div', { "class": styles["actionbar-right"] }, this.renderActions(this.$props.rightActions)),
        ])
    }
})

export type ActionBarType = InstanceType<typeof ActionBar>

interface AlertInterface {
    alertId: string;
    isHide: boolean;
    status: boolean;
    position: string;
    header: string;
    message: string;
}

interface AlertDataInterface {
    alerts: Array<AlertInterface>
}

export const Alert = defineComponent({
    name: "Alert",
    props: {
        top: { type: Number, default: 40 },
        bottom: { type: Number, default: 40 },
        width: { type: Number, default: 360 },
        duration: { type: Number, default: 300 },
        closeIn: { type: Number, default: null },
    },
    data(): AlertDataInterface {
        const num = Math.floor(Math.random() * (9999 - 1000) + 1000)
        const alertId = 'alert' + num.toString()
        const alert = {
            alertId: alertId,
            position: "top center",
            status: false,
            isHide: false,
            header: "",
            message: "",
        }
        return {
            alerts: [alert]
        };
    },
    methods: {
        defaultAlert() {
            const num = Math.floor(Math.random() * (9999 - 1000) + 1000)
            const alertId = 'alert' + num.toString()
            return {
                alertId: alertId,
                position: "top center",
                status: false,
                isHide: false,
                header: "",
                message: "",
            }
        },
        showAlert(
            alertMessage: string,
            alertHeader?: string,
            options?: { position?: string }
        ): void {
            const alert = this.alerts.slice(-1)[0]
            alert.header = alertHeader ? alertHeader : "";
            alert.message = alertMessage;
            if (options) {
                alert.position = options.position ? options.position : "top center";
            }
            this.alerts.push(this.defaultAlert())
            setTimeout(() => {
                alert.status = true;
            }, 50);
            if (this.closeIn) {
                setTimeout(() => this.closeAlert(alert), this.closeIn);
            }
        },

        closeAlert(alert: AlertInterface) {
            alert.isHide = true;
            setTimeout(() => {
                this.alerts = this.alerts.filter((item) => (item.alertId != alert.alertId))
            }, this.duration);
        },

        renderAlert(alert: AlertInterface) {
            const rootClasses = [styles["alert"]]
            for (const part of alert.position.split(" "))
                rootClasses.push(styles[part])
            if (alert.status) {
                if (!alert.isHide) {
                    rootClasses.push(styles["active"])
                }
            }

            const rootStyle: any = {
                width: this.width.toString() + "px",
                transition: "all " + this.duration.toString() + "ms ease-in-out"
            }
            if (alert.position.indexOf('top') > -1) {
                rootStyle["top"] = this.top.toString() + "px";
            }

            return h("div", { class: rootClasses, style: rootStyle },
                h("div", { class: styles["alert-container"] },
                    h('div', { class: styles["alert-content"] }, [
                        h('h5', { class: styles["alert-head"] }, alert.header),
                        h('p', { class: styles["alert-message"] }, alert.message)
                    ])
                ));
        },
    },
    render() {
        const children = []
        for (const alert of this.alerts) {
            children.push(this.renderAlert(alert))
        }
        return h('div', { "id": "alert-root" }, children)
    },
});

export type AlertType = InstanceType<typeof Alert>

export interface HeroAnnotationText {
    text: string;
    annotation: string;
}

export const Hero = defineComponent({
    name: 'Hero',
    props: {
        title: { type: String, default: "" },
        text: { type: String, default: "" },
        iamge_src: { type: String, default: "" },
        annotation_text: { type: Object as PropType<HeroAnnotationText>, default: undefined },
    },
    render() {
        if (this.annotation_text) {
            const textNodes: VNode[] = []
            let text = this.annotation_text.text.trim().split(' ')
            const annotation = this.annotation_text.annotation.trim().split(' ')
            if (text.length == 1) {
                text = text[0].split('')
            }
            const annotation_text_array = text.map((k, idx) => {
                if (idx < annotation.length) {
                    return [k, annotation[idx]]
                } else {
                    return [k, '']
                }
            })
            for (const item of annotation_text_array) {
                textNodes.push(h('div', { class: styles["hero-letter"] },
                    h('ruby', [
                        item[0],
                        h('rp', '('),
                        h('rt', item[1] || ''),
                        h('rp', ')')
                    ])
                ))
            }
            return h('div', { class: styles["hero-line"] }, textNodes)
        } else {
            const children = []
            if(this.iamge_src){
                children.push(h('img', {src: this.iamge_src}))
            }
            if(this.title){
                children.push(h('div', {class: styles["title"]}, this.title))
            }
            if(this.text){
                children.push(h('div', {}, this.text))
            }
            return h('div', { class: styles["h-hero"] }, children)
        }

    }
});


export const AnnotationText = defineComponent({
    name: 'AnnotationText',
    props: {
        text: { type: String, default: "" },
        annotation: { type: String, default: "" },
    },
    render() {
        const textNodes: VNode[] = []
        const text = this.text.trim().replace(' ', '').split('')
        const annotation = this.annotation.trim().split(' ')
        const annotation_text_array = text.map((k, idx) => {
            if (idx < annotation.length) {
                return [k, annotation[idx]]
            } else {
                return [k, '']
            }
        })
        for (const item of annotation_text_array) {
            textNodes.push(h('div', { class: styles["annotation-text"] },
                h('ruby', [
                    item[0],
                    h('rp', '('),
                    h('rt', item[1] || ''),
                    h('rp', ')')
                ])
            ))
        }
        return h('div', { class: styles["annotation-text-line"] }, textNodes)
    }
});

export const Row = defineComponent({
    name: 'Row',
    props: {
        justify: { type: String, default: "start" },
        align: { type: String, default: "center" },
        width_size: { type: Number, default: -1}
    },
    render() {
        const style = { "justify-content": this.justify, "align-items": this.align}
        const viewClasses = [styles["row"]]

        if (this.width_size >= 0){
            const sizeName = get_size_name(this.$props.width_size)
            viewClasses.push(styles[`w_${sizeName}`])
        }
        return h('div', { class: viewClasses,
            style: style
        }, renderSlot(this.$slots, "default", {}))
    }
});

export const Column = defineComponent({
    name: 'Column',
    props: {
        justify: { type: String, default: "start" },
        align: { type: String, default: "center" },
        height_size: { type: Number, default: -1},
        width_size: { type: Number, default: -1}
    },
    render() {
        const style = { "justify-content": this.justify, "align-items": this.align}
        const viewClasses = [styles["column"]]

        if (this.height_size >= 0){
            const sizeName = get_size_name(this.$props.height_size)
            viewClasses.push(styles[`h_${sizeName}`])
        }

        if (this.width_size >= 0){
            const sizeName = get_size_name(this.$props.width_size)
            viewClasses.push(styles[`w_${sizeName}`])
        }

        return h('div', { class: viewClasses,
            style: style
        }, renderSlot(this.$slots, "default", {}))
    }
});

export interface MenuItem {
    text: string
    sub_text?: string
    disable?: boolean
    disable_text?: string
    icon?: string
    name?: string
    clicked?: Function
}

export const NavMenu = defineComponent({
    name: 'NavMenu',
    props: {
        size: { type: Number },
        h_size: { type: Number, default: 3 },
        v_size: { type: Number, default: 3 },
        text_size: { type: Number, default: 3 },
        icon_size: { type: Number, default: 3 },
        icon_pos: { type: String, default: "left" },
        gap: { type: Number, default: 3 },
        items: { type: Array as PropType<Array<MenuItem>>, default: [] }
    },
    emits: {
        menuItemClicked: (name: string) => { return true },
    },
    render() {
        const h_size = this.size ?? this.h_size
        const v_size = this.size ?? this.v_size
        const items: VNode[] = []
        for (const item of this.items) {
            items.push(h(Button, {
                icon: item.icon,
                text: item.text,
                sub_text: item.sub_text,
                disable: item.disable,
                disable_text: item.disable_text,
                h_size: h_size,
                text_size: this.text_size,
                v_size: v_size,
                icon_size: this.icon_size,
                icon_pos: this.icon_pos,
                onClicked: () => {
                    if (item.clicked) {
                        item.clicked()
                    }
                    if (item.name) {
                        this.$emit("menuItemClicked", item.name)
                    }

                }
            }))
        }
        return h('div', { class: styles["main-menu"] }, items)
    }
});

export interface CountWrapper {
    count: number
}

export const IconCountText = defineComponent({
    name: 'IconCountText',
    props: {
        icon: { type: String, default: "" },
        animate: { type: Boolean, default: true },
        wrapper: { type: Object as PropType<CountWrapper>, required: true }
    },
    data() {
        return {
            tweened: this.wrapper.count
        }
    },
    computed: {
        count() {
            return this.wrapper.count
        }
    },
    watch: {
        count(n) {
            if (this.animate) {
                gsap.to(this, { duration: 0.5, tweened: Number(n) || 0 })
            } else {
                this.tweened = this.count
            }

        }

    },
    render() {
        return h(IconNumberText, {
            class: styles["currency-text"],
            icon: this.icon,
            number: Math.floor(this.tweened),
        })
    }
});

export const ProgressBar = defineComponent({
    name: 'ProgressBar',
    props: {
        percent: {type: Number, default: -1},
        value: { type: Number, default: -1},
        total: { type: Number, default: -1},
        width_size: { type: Number, default: -1}
    },
    render() {
        const viewClasses = [styles["progress-bar"]]
        const sizeName = get_size_name(this.$props.width_size)
        if(this.width_size >= 0){
            viewClasses.push(styles[`w_${sizeName}`])
        }
        let progress_text = ""
        let progress_percent = "0%"
        if(this.value >= 0 && this.total > 0){
            let percent_value = Math.floor((this.value*100)/this.total)
            if(percent_value > 100){
                percent_value = 100
            }
            progress_text = `${this.value}/${this.total}`
            progress_percent = `${percent_value}%`

        } else if(this.percent >= 0){
            let percent_value = Math.floor(this.percent)
            progress_text = `${percent_value}%`
            if(percent_value > 100){
                progress_percent = "100%"
            } else {
                progress_percent = progress_text
            }

        }
        return  h('div', { class: viewClasses },
                    h('div', { class: styles["progress"], style: {"width": progress_percent}},
                        h('div', { class: styles["progress-text"]}, progress_text)
                    )
                )
    }
});

export const StarRating = defineComponent({
    name: 'StarRating',
    props: {
        rating: { type: Number, default: 1 },
        icon: { type: String, default: "assets/common/star_full.png" },
        animate: { type: Boolean, default: true }
    },
    render() {
        const nodes = []
        for (let i = 0; i < this.rating; i++) {
            nodes.push(h('img', {
                src: this.icon,
                "class": `animate__animated animate__bounceIn animate__faster`,
                "style": { "animation-delay": `${i * 400}ms` }
            }))
        }
        return h('div', {
            class: styles["icon-title"]
        }, nodes)
    }
});

export const IconTitle = defineComponent({
    name: 'IconTitle',
    props: {
        icon: { type: String },
        count: { type: Number, default: 3 }
    },
    computed: {
        iconUrl() {
            return this.icon ?? "";
        }
    },
    render() {
        const nodes = []
        for (let i = 0; i < this.count; i++) {
            nodes.push(h('img', { src: this.iconUrl }))
        }
        return h('div', {
            class: styles["icon-title"]
        }, nodes)
    }
});

export const Icon = defineComponent({
    name: 'Icon',
    props: {
        icon: { type: String, default: "" },
        size: { type: Number, default: 3}
    },

    render() {
        const children: VNode[] = []
        const inline_style: Record<string, any> = {}
        const viewClasses = [styles["icon"]]
        const sizeName = get_size_name(this.$props.size)
        viewClasses.push(styles[sizeName])
        if (this.icon) {
            children.push(h('img', { src: this.icon }))
        }

        return h('div', { class: viewClasses, style: inline_style }, children)
    }
});


export const IconText = defineComponent({
    name: 'IconText',
    props: {
        text: { type: String, default: "" },
        icon: { type: String, default: "" },
        hint: { type: String, default: "" },
        text_weight: { type: String, default: "" }
    },

    render() {
        const children: VNode[] = []
        const inline_style: Record<string, any> = {}
        if (this.text_weight) {
            inline_style['font-weight'] = this.text_weight
        }
        if (this.icon) {
            children.push(h('img', { src: this.icon }))
        }
        children.push(h('div', this.text))
        if (this.hint) {
            children.push(h('div', { class: styles["hint-text"] }, `(${this.hint})`))
        }

        return h('div', { class: styles["item-name"], style: inline_style }, children)
    }
});


export const TableView = defineComponent({
    name: 'TableView',

    props: {
        columns: { type: Array, default: [] },
        showHeader: { type: Boolean, default: true },
        showInnerColumn: { type: Boolean, default: false },
        showInnerRow: { type: Boolean, default: true },
        rows: { type: Array, default: [] },
        cellRender: { type: Function, default: (cell: any) => { return h('div'); } }
    },
    computed: {
        columnCount() {
            return this.$props.columns.length;
        }
    },

    render() {
        const body: VNode[] = []
        for (const row of this.rows) {
            const row_rendered: VNode[] = []
            if (Array.isArray(row)) {
                for (const [idx, cell] of row.entries()) {
                    if (idx >= this.columnCount) {
                        break;
                    }
                    row_rendered.push(h('td', { class: styles["table-td"] }, this.cellRender(cell)))
                }
            } else {
                row_rendered.push(h('td', { class: styles["table-td"] }, this.cellRender(row)))
            }
            body.push(h('tr', { class: styles["table-tr"] }, row_rendered))
        }
        return h('div', {},
            h('table', { class: styles["table-view"] }, [
                h('tbody', {}, body)
            ])
        )
    }
});


export const Logo = defineComponent({
    name: 'Logo',
    props: {
        text: { type: String, default: ""},
        image_src: { type: String, default: ""}
    },

    render() {
        const children = []
        children.push(h('img', {class: styles['h-logo'], src: this.image_src}))
        if(this.text){
            children.push(h('div', {class: styles['h-logo-text']}, this.text))
        }
        return h('a', { class: [styles["h-row"]]}, children)
    }
});


export const InputText = defineComponent({
    name: 'InputText',
    props: {
        label: { type: String, default: ""},
        name: { type: String, default: ""},
        password: { type: Boolean, Default: false}
    },

    data() {
        return {
            "text": ""
        }
    },

    emits: {
        textChanged: (text: string) => {return true;}
    },

    methods: {
        valueChanged(value: string) {
            this.text = value
            this.$emit("textChanged", value)
        }
    },
    render() {
        const children = []
        let name = this.name
        if(name.length == 0){
            name = randomString(12)
        }
        if(this.label){
            children.push(h('label', {
                for: name,
                class:[styles["h-form-label"]]
            }, this.label))
        }
        if(this.password){
            children.push(h(PrimePassword, {
                id: name,
                class:[styles["h-form-element"]],
                toggleMask: true,
                modelValue: this.text,
                "onUpdate:modelValue": this.valueChanged
            }))
        } else {
            children.push(h(PrimeInputText, {id: name,
                class:[styles["h-form-element"]],
                modelValue: this.text,
                "onUpdate:modelValue": this.valueChanged
            }))
        }

        return h('div', { class: [styles["h-form-line"]]}, children)
    }
});

export const Card = defineComponent({
    name: 'Card',
    props: {
        title: { type: String, default: "" },
        sub_title: { type: String, default: "" },
        text: { type: String, default: ""},
        image_src: { type: String, default: ""},
        showBorder: { type: Boolean, default: true },
        style: { type: Object, default: {}},
    },

    render() {
        const content_hint_tags = this.style.content_hint_tags ?? []
        return h(PrimeCard, { class: [styles["card"], styles["h-card"]] }, {
            "header": () => {
                return h('img', {src: this.image_src})
            },
            "title": () => {
                return this.title
            },
            "subtitle": () => {
                return this.sub_title
            },
            "content": () => {
                return h('div', { class: [styles['h-content'], ...content_hint_tags]}, [
                    h('p', this.text),
                    renderSlot(this.$slots, "default", {})
                ])
            }

        })
    }
});

export const CardSwiper = defineComponent({
    name: 'CardSwiper ',
    props: {
        title: { type: String, default: "" },
        cards: { type: Array, default: [] },
        cardRender: { type: Function, default: (cell: any) => { return h('div'); } }
    },
    render() {
        return h(Swiper, {
            class: styles["card-swiper"],
            effect: "cards",
            grabCursor: true,
            modules: [EffectCards],
        }, {
            default: () => {
                const body: VNode[] = []
                for (const card of this.cards) {
                    body.push(h(SwiperSlide, { class: styles["card-swiper-slide"] }, {
                        default: () => {
                            return this.cardRender(card);
                        }
                    }))
                }
                return body
            },
            _: 1  //DO NOT delete this line, it will influr vue performance
        })
    }
});

export const Loader = defineComponent({
    name: 'Loader',
    render() {
        return h('span', {
            class: styles["loader"]
        })
    }
});

export const ImageView = defineComponent({
    name: 'ImageView',
    props: {
        image_url: { type: String, default: "" },
        image_type: { type: String, default: "image/jpeg" },
        size: { type: Number, default: 3 }
    },
    render() {
        const viewClasses = [styles["image-view"]]
        const sizeName = get_size_name(this.$props.size)
        viewClasses.push(styles[sizeName])

        return h('img', {
            src: this.image_url,
            crossorigin: "anonymous",
            class: viewClasses,
            "style": {
                "max-height": "100%",
                "max-width:": "100%",
                "object-fit": "cover"
            }
        })
    }
});

export const VideoPlayer = defineComponent({
    name: 'VideoPlayer',
    props: {
        video_url: { type: String, default: "" },
        poster_url: { type: String, default: "" },
        video_type: { type: String, default: "video/mp4" },
        aspect: { type: String, default: "8:5" },
        autoplay: { type: Boolean, default: true },
        muted: { type: Boolean, default: true },
        width: { type: Number, default: 300 },
        height: { type: Number, default: 400 },
        size: { type: Number, default: 3 }
    },
    render() {
        const playerClasses = [styles["video-player"]]
        const sizeName = get_size_name(this.$props.size)
        playerClasses.push(styles[sizeName])

        return h(VideoJSVideoPlayer, {
            src: this.video_url,
            poster: this.poster_url,
            controls: true,
            muted: this.muted,
            preload: 'auto',
            autoplay: this.autoplay,
            crossorigin: "anonymous",
            width: this.width,
            height: this.height,
            disablePictureInPicture: true,
            class: playerClasses
        })
    }
});

export const RichText = defineComponent({
    name: 'RichText',
    props: {
        text: { type: String, default: "" }
    },
    computed: {
        text_parts() {
            const text_parts = new RichTextCompiler().compile(this.text)
            return text_parts
        }
    },
    methods: {
        renderPart(part: RichTextPart) {
            if (part.text === '\n') {
                return h('br')
            } else if (part.tags.length == 0) {
                const style: any = {
                    "line-height": 1.5
                }
                return h('span', { style: style }, part.text)
            } else {
                const style: any = {
                    "line-height": 1.5
                }
                let text_node = undefined
                for (const tag of part.tags) {
                    if (tag.name === 'b') {
                        style["font-weight"] = "bold"
                    } else if (tag.name === 'i') {
                        style["font-style"] = "italic"
                    } else if (tag.name === 'u') {
                        if (text_node) {
                            text_node = h('u', {}, text_node)
                        } else {
                            text_node = h('u', {}, part.text)
                        }
                    } else if (tag.name === 's') {
                        if (text_node) {
                            text_node = h('s', {}, text_node)
                        } else {
                            text_node = h('s', {}, part.text)
                        }
                    } else if (tag.name === 'color') {
                        const color_attr = tag.attributes["color"]
                        const color = get_text_color(color_attr)
                        if (color) {
                            style['color'] = color
                        } else {
                            style['color'] = color_attr
                        }
                    } else if (tag.name === 'size') {
                        const size = parseInt(tag.attributes["size"])
                        const ratio = get_size_ratio(size)
                        style["font-size"] = `${ratio}em`
                    } else if (tag.name === 'link') {

                    } else if (tag.name === 'icon') {
                        return h('span', {}, h('img', {
                            style: { height: "1.1em", "vertical-align": "middle"},
                            src: tag.attributes['src']
                        }))
                    } else if (tag.name === 'image') {

                    } else if (tag.name === 'video') {

                    } else if (tag.name === 'quote') {

                    } else if (tag.name === 'list') {

                    }
                }
                if (text_node) {
                    return h('span', { style: style }, text_node)
                } else {
                    return h('span', { style: style }, part.text)
                }

            }
        }
    },
    render() {
        const nodes = []
        for (const part of this.text_parts) {
            nodes.push(this.renderPart(part as RichTextPart))
        }
        return h('div', {}, nodes)
    }
});
