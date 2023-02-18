import NoSsr from '@/components/NoSsr';
import React from 'react';

export default function App() {
    const Plot = React.lazy(() => import('react-plotly.js'));
    return (<NoSsr>
        <Plot
            data={[
                {
                    x: [1, 2, 3],
                    y: [2, 6, 3],
                    type: 'scatter',
                    mode: 'lines+markers',
                    marker: { color: 'red' },
                },
                { type: 'bar', x: [1, 2, 3], y: [2, 5, 3] },
            ]}
            layout={{ width: 320, height: 240, title: 'A Fancy Plot' }}
        />
    </NoSsr>)
}