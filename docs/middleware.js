export const config = {
  matcher: ['/', '/index', '/index.html', '/supernet', '/supernet.html'],
};

export default function middleware(request) {
  const url = new URL(request.url);
  let path = url.pathname || '/';
  if (path.length > 1 && path.endsWith('/')) path = path.slice(0, -1);
  const dest = new URL('/api/root', url);
  dest.search = url.search;
  if (path === '/supernet' || path === '/supernet.html') {
    dest.searchParams.set('projection', 'panzoom');
  }
  const headers = new Headers();
  headers.set('x-middleware-rewrite', dest.toString());
  return new Response(null, { headers });
}
