/**
 * Генерирует случайную строку заданной длины
 * @param length Длина генерируемой строки
 * @returns Случайная строка
 */
function generateRandomString(length: number): string {
    const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    let result = ''
    const values = new Uint32Array(length)
    crypto.getRandomValues(values)
    for (let i = 0; i < length; i++) {
        result += charset[values[i] % charset.length]
    }
    return result
}

/**
 * Генерирует API ключ в формате "prefix_random-string"
 * @returns API ключ
 */
export function generateApiKey(): string {
    const prefix = 'sk'
    const randomPart = generateRandomString(32)
    return `${prefix}_${randomPart}`
}

/**
 * Маскирует API ключ, оставляя видимыми только первые и последние символы
 * @param key API ключ
 * @returns Маскированный ключ
 */
export function maskApiKey(key: string): string {
    if (key.length <= 8) return key
    const prefix = key.slice(0, 4)
    const suffix = key.slice(-4)
    return `${prefix}...${suffix}`
}
