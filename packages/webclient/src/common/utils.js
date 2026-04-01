const nargs = /\{([0-9a-zA-Z_\.]+)\}/g

export function format(str, ...values) {
  let args = {}
  args = values[0]

  if (!args || !args.hasOwnProperty) {
    args = {}
  }

  return str.replace(nargs, function replaceArg(match, i, index) {
    if (str[index - 1] === '{' && str[index + match.length] === '}') {
      return i
    }

    const parts = i.split('.')
    let _args = args
    for (const part of parts) {
      _args = _args.hasOwnProperty(part) ? _args[part] : {}
    }

    const result = _args

    if (result === null || result === undefined) {
      return ''
    }

    return result
  })
}

export function deepSet(target, key, value, separator = '.') {
  const parts = String(key).split(separator)
  let obj = target
  for (let i = 0; i < parts.length - 1; i += 1) {
    const current = parts[i]
    const next = parts[i + 1]
    const pvalue = next === `${parseInt(next, 10)}` ? [] : {}
    obj[current] = pvalue
    obj = pvalue
  }
  const current = parts[parts.length - 1]
  obj[current] = value
}
