import { Checkbox, TextField } from "@/components/Form";
import { selectConfig, setConfig } from "@/store/configSlice";
import { selectCredential, setCredential } from "@/store/credentialSlice";
import { useAppDispatch, useAppSelector } from "@/store/store";
import RootLayout from "./layout";

export default function Settings() {
    const dispatch = useAppDispatch();
    const credential = useAppSelector(selectCredential);
    const { username = "", password = "" } = credential;
    const config = useAppSelector(selectConfig);
    const { weighted, normalize, notify, backendUrl } = config;

    const onUsernameChange = (value: string) => {
        dispatch(setCredential({ username: value, password }));
    };

    const onPasswordChange = (value: string) => {
        dispatch(setCredential({ username, password: value }));
    };

    const onWeightedChange = (value: boolean) => {
        dispatch(setConfig({ ...config, weighted: value }));
    };

    const onNormalizeChange = (value: boolean) => {
        dispatch(setConfig({ ...config, normalize: value }));
    };

    const onNotifyChange = (value: boolean) => {
        dispatch(setConfig({ ...config, notify: value }));
    };

    const onBackendUrlChange = (value: string) => {
        dispatch(setConfig({ ...config, backendUrl: value }));
    };

    return (
        <RootLayout>
            <div className="grid grid-cols-1 gap-8">
                <TextField
                    id="username"
                    value={username}
                    label="Username for eClass Login"
                    onChange={onUsernameChange}
                />
                <TextField
                    id="password"
                    value={password}
                    label="Password for eClass Login"
                    onChange={onPasswordChange}
                />
                <Checkbox
                    id="weighted"
                    checked={weighted}
                    label="Weighted grades (+10 for AP)"
                    onChange={onWeightedChange}
                />
                <Checkbox
                    id="normalize"
                    checked={normalize}
                    label="Normalize grades"
                    onChange={onNormalizeChange}
                />
                <Checkbox
                    id="notify"
                    checked={notify}
                    label="Notify when grades are updated"
                    onChange={onNotifyChange}
                />
                <TextField
                    id="backend-url"
                    value={backendUrl || ""}
                    label="Backend URL"
                    onChange={onBackendUrlChange}
                />
            </div>
        </RootLayout>
    );
}
