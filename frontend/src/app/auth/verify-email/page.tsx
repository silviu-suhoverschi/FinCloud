'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import authService from '@/lib/auth'

export default function VerifyEmailPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const token = searchParams.get('token')

  const [isVerifying, setIsVerifying] = useState(false)
  const [isVerified, setIsVerified] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const verifyEmail = async (verificationToken: string) => {
      setIsVerifying(true)
      setError(null)

      try {
        await authService.verifyEmail({ token: verificationToken })
        setIsVerified(true)
        setTimeout(() => {
          router.push('/auth/login')
        }, 3000)
      } catch (err: any) {
        setError(
          err.response?.data?.detail ||
            'Email verification failed. The link may have expired or is invalid.'
        )
      } finally {
        setIsVerifying(false)
      }
    }

    if (token) {
      verifyEmail(token)
    } else {
      setError('Verification token is missing. Please check your email link.')
    }
  }, [token, router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 px-4">
      <div className="max-w-md w-full">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
              FinCloud
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">Email verification</p>
          </div>

          <div className="text-center">
            {isVerifying && (
              <div className="py-8">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <p className="mt-4 text-gray-600 dark:text-gray-400">Verifying your email...</p>
              </div>
            )}

            {isVerified && (
              <div className="py-8">
                <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 dark:bg-green-900/20">
                  <svg
                    className="h-6 w-6 text-green-600 dark:text-green-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </div>
                <h2 className="mt-4 text-xl font-semibold text-gray-900 dark:text-white">
                  Email verified successfully!
                </h2>
                <p className="mt-2 text-gray-600 dark:text-gray-400">
                  Redirecting you to the login page...
                </p>
              </div>
            )}

            {error && (
              <div className="py-8">
                <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 dark:bg-red-900/20">
                  <svg
                    className="h-6 w-6 text-red-600 dark:text-red-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </div>
                <h2 className="mt-4 text-xl font-semibold text-gray-900 dark:text-white">
                  Verification failed
                </h2>
                <p className="mt-2 text-red-600 dark:text-red-400">{error}</p>
                <div className="mt-6 space-y-3">
                  <Link
                    href="/auth/register"
                    className="block w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition duration-200"
                  >
                    Create new account
                  </Link>
                  <Link
                    href="/auth/login"
                    className="block w-full py-2 px-4 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium rounded-lg transition duration-200 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
                  >
                    Go to login
                  </Link>
                </div>
              </div>
            )}

            {!token && !error && (
              <div className="py-8">
                <p className="text-gray-600 dark:text-gray-400">
                  Please check your email for the verification link.
                </p>
                <Link
                  href="/auth/login"
                  className="mt-6 inline-block py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition duration-200"
                >
                  Go to login
                </Link>
              </div>
            )}
          </div>
        </div>

        <div className="mt-4 text-center">
          <Link href="/" className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400">
            ← Back to home
          </Link>
        </div>
      </div>
    </div>
  )
}
