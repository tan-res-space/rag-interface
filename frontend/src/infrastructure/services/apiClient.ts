/**
 * API Client for Speaker Profile Service
 * Uses the existing BaseApi pattern from the codebase
 */

import { BaseApi } from '@infrastructure/api/base-api';

interface ApiResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
}

interface RequestConfig {
  params?: Record<string, any>;
  headers?: Record<string, string>;
}

class ApiClient extends BaseApi {
  async get<T>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    try {
      // Build query string from params
      let fullUrl = url;
      if (config?.params) {
        const searchParams = new URLSearchParams();
        Object.entries(config.params).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            searchParams.append(key, String(value));
          }
        });
        const queryString = searchParams.toString();
        if (queryString) {
          fullUrl += (url.includes('?') ? '&' : '?') + queryString;
        }
      }

      const response = await fetch(`${this.baseURL}${fullUrl}`, {
        method: 'GET',
        headers: {
          ...this.getHeaders(),
          ...config?.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      return {
        data,
        status: response.status,
        statusText: response.statusText,
      };
    } catch (error) {
      console.error('API GET request failed:', error);
      throw error;
    }
  }

  async post<T>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    try {
      // Build query string from params
      let fullUrl = url;
      if (config?.params) {
        const searchParams = new URLSearchParams();
        Object.entries(config.params).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            searchParams.append(key, String(value));
          }
        });
        const queryString = searchParams.toString();
        if (queryString) {
          fullUrl += (url.includes('?') ? '&' : '?') + queryString;
        }
      }

      const response = await fetch(`${this.baseURL}${fullUrl}`, {
        method: 'POST',
        headers: {
          ...this.getHeaders(),
          ...config?.headers,
        },
        body: data ? JSON.stringify(data) : undefined,
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      const responseData = await response.json();
      
      return {
        data: responseData,
        status: response.status,
        statusText: response.statusText,
      };
    } catch (error) {
      console.error('API POST request failed:', error);
      throw error;
    }
  }

  async put<T>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseURL}${url}`, {
        method: 'PUT',
        headers: {
          ...this.getHeaders(),
          ...config?.headers,
        },
        body: data ? JSON.stringify(data) : undefined,
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      const responseData = await response.json();
      
      return {
        data: responseData,
        status: response.status,
        statusText: response.statusText,
      };
    } catch (error) {
      console.error('API PUT request failed:', error);
      throw error;
    }
  }

  async delete<T>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseURL}${url}`, {
        method: 'DELETE',
        headers: {
          ...this.getHeaders(),
          ...config?.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      const responseData = await response.json();
      
      return {
        data: responseData,
        status: response.status,
        statusText: response.statusText,
      };
    } catch (error) {
      console.error('API DELETE request failed:', error);
      throw error;
    }
  }
}

// Create and export the API client instance
export const apiClient = new ApiClient();
