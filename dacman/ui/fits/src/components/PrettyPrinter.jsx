import React from "react";

export function PrettyPrinter({ item }) {
    return (
        <div>
            <code>
                <pre>
                    {JSON.stringify(item, null, '  ')}
                </pre>
            </code>
        </div>
    );
}
