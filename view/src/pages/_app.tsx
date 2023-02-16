import { ReactElement } from 'react';
import './global.css'

interface AppProps {
    Component: React.ElementType;
    pageProps: Record<string, unknown>;
}

export default function App({ Component, pageProps }: AppProps): ReactElement {
    return <Component {...pageProps} />;
}
