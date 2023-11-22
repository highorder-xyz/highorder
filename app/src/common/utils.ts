
const nargs = /\{([0-9a-zA-Z_\.]+)\}/g

export function format(str: string, ...values: Record<string, any>[]) {
    let args: Record<string, any> = {}

    args = values[0]

    if (!args || !args.hasOwnProperty) {
        args = {}
    }

    return str.replace(nargs, function replaceArg(match, i, index) {
        var result

        if (str[index - 1] === "{" &&
            str[index + match.length] === "}") {
            return i
        } else {
            const parts = i.split(".")
            let result = undefined
            let _args = args
            for (const part of parts) {
                _args = _args.hasOwnProperty(part) ? _args[part] : {}
            }
            result = _args

            if (result === null || result === undefined) {
                return ""
            }

            return result
        }
    })
}

export function deepSet(target: any, key: string, value: any, separator: string = '.') {
    const parts: Array<string> = key.split(separator)
    let obj: any = target
    for (let i = 0; i < parts.length - 1; i++) {
        const current = parts[i]
        const next = parts[i + 1]
        const pvalue = next === `${parseInt(next, 10)}` ? [] : {};
        obj[current] = pvalue
        obj = pvalue
    }
    const current = parts[parts.length - 1]
    obj[current] = value
}