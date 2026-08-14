// app/lib/core/services/api_client.dart

import 'dart:async';
import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

/// Exception thrown by ApiClient with sanitized user-friendly error messages.
class AppException implements Exception {
  final String message;
  final int? statusCode;
  final bool isNetworkError;

  AppException(this.message, {this.statusCode, this.isNetworkError = false});

  @override
  String toString() => message;
}

/// Controlled single API layer for Flutter learning application.
/// Routes all requests through backend REST services (http://localhost:8000/api).
/// Flutter MUST NEVER call ContentAgent or external AI providers directly.
class ApiClient {
  late final Dio _dio;
  final String learnerId;
  final String adminKey;

  ApiClient({
    String? baseUrl,
    this.learnerId = 'user_default_01',
    this.adminKey = 'secret_admin_key_123',
  }) {
    final configuredUrl = baseUrl ?? dotenv.env['BACKEND_URL'] ?? 'http://localhost:8000/api';

    _dio = Dio(
      BaseOptions(
        baseUrl: configuredUrl,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 25),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'x-learner-id': learnerId,
          'x-admin-key': adminKey,
        },
      ),
    );

    // Logging & Sanitizing Interceptor
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          if (kDebugMode) {
            debugPrint('API Request [${options.method}] -> ${options.path}');
          }
          return handler.next(options);
        },
        onResponse: (response, handler) {
          return handler.next(response);
        },
        onError: (DioException error, handler) {
          final mappedException = _mapDioError(error);
          return handler.reject(
            DioException(
              requestOptions: error.requestOptions,
              error: mappedException,
              response: error.response,
              type: error.type,
            ),
          );
        },
      ),
    );
  }

  AppException _mapDioError(DioException error) {
    if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout ||
        error.type == DioExceptionType.connectionError) {
      return AppException(
        'Unable to connect to learning server. Please check your internet connection.',
        isNetworkError: true,
      );
    }

    final statusCode = error.response?.statusCode;
    if (statusCode == 403) {
      return AppException('Access denied or ownership restriction.', statusCode: 403);
    } else if (statusCode == 404) {
      return AppException('Requested learning resource was not found.', statusCode: 404);
    } else if (statusCode == 429) {
      return AppException('Rate limit exceeded. Please wait a moment before retrying.', statusCode: 429);
    } else if (statusCode != null && statusCode >= 500) {
      return AppException('Learning server encountered a temporary issue. Please try again.', statusCode: statusCode);
    }

    return AppException('An unexpected error occurred. Please try again.', statusCode: statusCode);
  }

  Future<dynamic> get(String path, {Map<String, dynamic>? queryParameters}) async {
    try {
      final response = await _dio.get(path, queryParameters: queryParameters);
      return response.data;
    } on DioException catch (e) {
      throw e.error is AppException ? e.error as AppException : _mapDioError(e);
    } catch (e) {
      throw AppException('Failed to parse server response.');
    }
  }

  Future<dynamic> post(String path, {dynamic data, Map<String, dynamic>? queryParameters}) async {
    try {
      final response = await _dio.post(path, data: data, queryParameters: queryParameters);
      return response.data;
    } on DioException catch (e) {
      throw e.error is AppException ? e.error as AppException : _mapDioError(e);
    } catch (e) {
      throw AppException('Failed to send request to server.');
    }
  }

  Future<dynamic> put(String path, {dynamic data, Map<String, dynamic>? queryParameters}) async {
    try {
      final response = await _dio.put(path, data: data, queryParameters: queryParameters);
      return response.data;
    } on DioException catch (e) {
      throw e.error is AppException ? e.error as AppException : _mapDioError(e);
    } catch (e) {
      throw AppException('Failed to update resource on server.');
    }
  }

  Future<dynamic> delete(String path, {Map<String, dynamic>? queryParameters}) async {
    try {
      final response = await _dio.delete(path, queryParameters: queryParameters);
      return response.data;
    } on DioException catch (e) {
      throw e.error is AppException ? e.error as AppException : _mapDioError(e);
    } catch (e) {
      throw AppException('Failed to delete resource on server.');
    }
  }
}
