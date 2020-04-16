
function getFiles() {
    const data = [
        {
            path: '/foo/bar/baz',
            key: '/foo/bar/baz',
            isDir: true
        },
        {
            path: '/foo/bar/baz/base.fits',
            key: '/foo/bar/baz/base.fits',
            type: 'fits'
        },
        {
            path: '/foo/bar/baz/base.csv',
            key: '/foo/bar/baz/base.csv',
            type: 'csv'
        },
        {
            path: '/foo/bar/baz/base.hdf5',
            key: '/foo/bar/baz/base.hdf5',
            type: 'hdf5',
        },
    ];

    return data;
}

function getFitsHDUs() {
    return {
        A: [
            {
                extension: 0,
                name: 'PRIMARY',
                hdu_type: 'Image',
                dimensions: '(4645, 1000)',
                content_type: 'spectrum'
            },
            {
                extension: 1,
                name: 'IVAR',
                hdu_type: 'Image',
                dimensions: '(4645, 1000)',
            },
            {
                extension: 2,
                name: 'PLUGMAP',
                hdu_type: 'BinTable',
                dimensions: '1000r x 35c',
            },
        ],
        B: [
            {
                extension: 0,
                name: 'PRIMARY',
                hdu_type: 'Image',
                dimensions: '(4645, 1000)',
                content_type: 'spectrum'
            },
            {
                extension: 1,
                name: 'IVAR',
                hdu_type: 'Image',
                dimensions: '(4645, 1000)',
            },
        ]
    }
}

function getComparison() {
    return [
        {
            type: "files",
            data: getFiles(),
            labels: {
                A: 'foo',
                B: 'bar',
            }
        },
        {
            type: "fits",
            data: getFitsHDUs().A,
        },
        {
            type: "fits",
            data: getFitsHDUs().B,
        }
    ];
}

// get data for multiple comparisons that are being worked on
// now used to populate the sidebar data
function getActiveComparisons() {
    return [
        {
            comparisonID: 1,
            fileA: "base.csv",
            fileB: "new.csv"
        },
        {
            comparisonID: 2,
            fileA: "base.fits",
            fileB: "new.fits"
         },
        {
            comparisonID: 3,
            fileA: "base.h5",
            fileB: "new.h5"
        },
        {
            comparisonID: 4,
            fileA: "base.txt",
            fileB: "new.txt"
        },
    ];
}

function getSummary() {
    const data = [
        {
            type: "counts",
            data: {
                total: 4452,
                added: 123,
                deleted: 45,
                modified: 12,
                unchanged: 3523,
            }
        },
        {
            type: "heatmap",
            data: {
                url: '/base/delta.png'
            }
        }
    ]

    return data;
}

export {
    getFiles,
    getSummary,
    getComparison,
    getActiveComparisons,
};
