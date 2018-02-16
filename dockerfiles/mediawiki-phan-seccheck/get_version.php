#!/usr/bin/env php
<?php
/**
 * Get phan-taint-check plugin version from composer.json's extra field
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 * http://www.gnu.org/copyleft/gpl.html
 *
 * @file
 */

if ( file_exists( 'composer.json' ) ) {
    $json = json_decode( file_get_contents( 'composer.json' ), true );
    if ( isset( $json['extra']['phan-taint-check-plugin'] ) ) {
        echo $json['extra']['phan-taint-check-plugin'];
        exit;
    }
}

// Fallback to default:
echo '1.1.0';


