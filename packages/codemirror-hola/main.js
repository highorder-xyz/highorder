
import { hola_editor } from './src/index'

const hello_code = `
Page {
    Hero {
        name: "strhe"
        p: true
        l: false
        i: 123
        Image {
            urls: [
            "http://xx", 'http://' //urls of image
            ]
        }
    }
}
`
hola_editor({
    code: hello_code,
    parent_id: "app",
    changed_cb: (code) => {
        console.log('changed. sync to server.')
    }
})