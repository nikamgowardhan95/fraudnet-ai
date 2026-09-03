import { NextRequest, NextResponse } from "next/server"

const BACKEND_URL = process.env.FRAUDNET_BACKEND_URL ?? "http://127.0.0.1:8000"

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params
  const target = `${BACKEND_URL}/${path.join("/")}${request.nextUrl.search}`
  const body = request.method === "GET" || request.method === "HEAD" ? undefined : await request.text()

  try {
    const response = await fetch(target, {
      method: request.method,
      headers: { "content-type": request.headers.get("content-type") ?? "application/json" },
      body,
      cache: "no-store",
    })
    return new NextResponse(response.body, { status: response.status, headers: { "content-type": response.headers.get("content-type") ?? "application/json" } })
  } catch {
    return NextResponse.json({ detail: "FraudNet backend is unavailable" }, { status: 503 })
  }
}

export const GET = proxy
export const POST = proxy
export const PUT = proxy
export const PATCH = proxy
export const DELETE = proxy
