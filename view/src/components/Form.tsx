type CheckboxProps = {
    id: string;
    checked: boolean;
    label: string;
    onChange: (value: boolean) => void;
};

export function Checkbox(props: CheckboxProps) {
    const checkboxStyle = `rounded
          border-gray-300
          text-indigo-600
          shadow-sm
          focus:border-sky-300
          focus:ring
          focus:ring-offset-0
          focus:ring-sky-200
          focus:ring-opacity-50`;

    return (
        <label htmlFor={props.id} className="block">
            <input
                type="checkbox"
                className={checkboxStyle}
                id={props.id}
                checked={props.checked}
                onChange={(e) => props.onChange(e.target.checked)}
            />
            <span className="ml-2 text-slate-700 font-medium">
                {props.label}
            </span>
        </label>
    );
}

type TextFieldProps = {
    id: string;
    value: string;
    label: string;
    onChange: (value: string) => void;
};

export function TextField(props: TextFieldProps) {
    const textStyle = `block
          w-full
          rounded-md
          border-gray-300
          shadow-sm
          focus:border-sky-300 focus:ring focus:ring-sky-200 focus:ring-opacity-50`;

    return (
        <label htmlFor={props.id} className="block">
            <span className="mb-1 text-slate-700 block font-medium">
                {props.label}
            </span>
            <input
                type="text"
                placeholder=""
                className={textStyle}
                id={props.id}
                value={props.value}
                onChange={(e) => props.onChange(e.target.value)}
            />
        </label>
    );
}
