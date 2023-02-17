export function cls(...args: string[]) {
    return args.filter(Boolean).join(" ");
}
