export type IconProps = {
    size: number;
};

export default function Logo({ size }: IconProps) {
    return (
        <img
            src="/favicon.png"
            alt="Better Gradebook"
            width={size}
            height={size}
        />
    );
}
