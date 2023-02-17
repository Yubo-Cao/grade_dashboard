import { ReactElement } from "react";
import { Provider } from "react-redux";
import store from "@/store/store";
import "./global.css";

interface AppProps {
    Component: React.ElementType;
    pageProps: Record<string, unknown>;
}

export default function App({ Component, pageProps }: AppProps): ReactElement {
    return (
        <Provider store={store}>
            <Component {...pageProps} />
        </Provider>
    );
}
