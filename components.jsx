import React from 'react';

// Typography Components
export const H2 = ({ children, id }) => (
  <h2 className="text-4xl font-bold my-4" id={id}>
    {children}
  </h2>
);

export const H3 = ({ children, id }) => (
  <h3 className="text-2xl font-bold my-4" id={id}>
    {children}
  </h3>
);

export const P = ({ children }) => (
  <p className="py-2 text-base">{children}</p>
);

export const Strong = ({ children }) => (
  <strong>{children}</strong>
);

export const Em = ({ children }) => (
  <em>{children}</em>
);

export const Link = ({ children, href }) => (
  <a className="text-blue-500 hover:underline cursor-pointer" href={href}>
    {children}
  </a>
);

// List Components
export const UL = ({ children }) => (
  <ul className="text-base list-disc pl-12 space-y-2 py-2">
    {children}
  </ul>
);

export const OL = ({ children }) => (
  <ol className="text-base list-decimal pl-12 space-y-2 py-2">
    {children}
  </ol>
);

export const LI = ({ children, id }) => (
  <li id={id}>{children}</li>
);

// Table Components
export const TableWrapper = ({ children }) => (
  <div style={{ overflowX: "auto", webkitOverflowScrolling: "touch" }}>
    {children}
  </div>
);

export const Table = ({ children }) => (
  <table className="text-base min-w-full border-collapse border border-gray-300 my-4">
    {children}
  </table>
);

export const THead = ({ children }) => (
  <thead className="text-center">{children}</thead>
);

export const TBody = ({ children }) => (
  <tbody>{children}</tbody>
);

export const TR = ({ children }) => (
  <tr>{children}</tr>
);

export const TH = ({ children }) => (
  <th className="px-4 py-2 border border-gray-300 font-semibold bg-gray-50">
    {children}
  </th>
);

export const TD = ({ children }) => (
  <td className="px-4 py-2 border border-gray-300">
    {children}
  </td>
);

// Media Components
export const Figure = ({ src, alt, caption, figNumber }) => (
  <div className="my-4">
    <img src={src} alt={alt} className="h-100 w-auto mx-auto" />
    <p className="text-sm text-center mt-2">
      <b>Fig {figNumber}.</b> {caption}
    </p>
  </div>
);
