---
date: 2022-02-22 14:05:22 +0900
layout: post
title: "[Jekyll] jekyll-theme-yat 테마를 사용하기 위한 기본 Setup"
tags: [Jekyll, jekyll-theme-yat, blog]
typora-root-url: ..
---

# 1. 개요

현재 이 블로그는 jekyll-theme-yat 테마를 사용 중이다.

해당 블로그를 꾸미기 위해 여러 가지 편집을 했는데, 어떤것을 했나?

* 향후 테마가 변경된다 해도 해당 게시물 편집을 하지 않음  



# 2. 설명

## 2.1 _config.yml

### (1). post url 변경

```_config.xml
permalink: /:categories/:title
```



### (2). header tag를 ToC 표시 시 적용 단계 변경

```conf
  header_offset: 1
```



### (3). post의 date 더 짧게 보여주기 위해서

```_config.yml
  date_format: "%Y-%m-%d"
```



### (4). copyright 실제 올바른 적용

```_config.yml
copyright: "Copyright 2015-{currentYear}. {author} All data cannot be copied without permission."
```



### (5). 블로그 기본 정보

```_config.yml
title: IT Blogger DongDong
email: ks900331@naver.com
author: DongHyun Kim
```



### (6). 블로그 URL

```_config.yml
url: "https://dhkim900331.github.io"
```



## 2.2 _data/defaults.yml

* 원래 _config.yml 입력 시 index.html 자동 컴파일 되어야 할 것으로 보이는데 해당 테마는 그렇지 않아 직접 변경

### (1). 사이트 정보

```_data/defaults.yml
<title>Home | IT Blogger DongDong</title>
<meta name="description" content="소프트웨어/솔루션/IT 엔지니어로 종사하며 얻는 모든 지식들을 공유하고자 블로그로 기록하고 있습니다. 제가 알고 있는 것을 공유하고 기록하는 행동을 통해, 많은 지식을 흡수하고 있습니다.">
<meta property="og:description" content="소프트웨어/솔루션/IT 엔지니어로 종사하며 얻는 모든 지식들을 공유하고자 블로그로 기록하고 있습니다. 제가 알고 있는 것을 공유하고 기록하는 행동을 통해, 많은 지식을 흡수하고 있습니다.">
```



## 2.3 _includes/head.html

### (1). favicon

```_includes/head.html
  <!-- original favicon tag -->
  <!--<link rel="shortcut icon" href="{{ site.favicon }}">-->
  
  <!-- tobe favicon tag (2022.02.22) -->
  <!-- https://hongpage.kr/28 -->
  <link rel="shortcut icon" href="/assets/img/favicons/favicon.ico">
  <link rel="apple-touch-icon" sizes="57x57" href="/assets/img/favicons/apple-icon-57x57.png">
  <link rel="apple-touch-icon" sizes="60x60" href="/assets/img/favicons/apple-icon-60x60.png">
  <link rel="apple-touch-icon" sizes="72x72" href="/assets/img/favicons/apple-icon-72x72.png">
  <link rel="apple-touch-icon" sizes="76x76" href="/assets/img/favicons/apple-icon-76x76.png">
  <link rel="apple-touch-icon" sizes="114x114" href="/assets/img/favicons/apple-icon-114x114.png">
  <link rel="apple-touch-icon" sizes="120x120" href="/assets/img/favicons/apple-icon-120x120.png">
  <link rel="apple-touch-icon" sizes="144x144" href="/assets/img/favicons/apple-icon-144x144.png">
  <link rel="apple-touch-icon" sizes="152x152" href="/assets/img/favicons/apple-icon-152x152.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/assets/img/favicons/apple-icon-180x180.png">
  <link rel="icon" type="image/png" sizes="192x192" href="/assets/img/favicons/android-icon-192x192.png">
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/img/favicons/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="96x96" href="/assets/img/favicons/favicon-96x96.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/assets/img/favicons/favicon-16x16.png">
  <link rel="manifest" href="/assets/img/favicons/manifest.json">
  <meta name="msapplication-TileColor" content="#ffffff">
  <meta name="msapplication-TileImage" content="/assets/img/favicons/ms-icon-144x144.png">
  <meta name="theme-color" content="#ffffff">
```



## 2.4 index.html

### (1). main banner image 변경 시 사용

```index.html
banner: "/assets/images/banners/home.jpeg"
```



## 2.5 _sass

* _site/assets/css/main.css 는 _sass 의 컴파일 결과물이므로, 변경하면 적용은 되지만 rebuild 할 때마다 새로이 컴파일 된 결과물이 덮어쓰기 되므로 원복된다.
* 그러므로 _sass 내 파일들을 변경해야 한다.

### (1). 기본 폰트 크기

* 해당 값에 의해 글로벌로 기준 폰트 크기로 사용된다.

```yat.scss
//$base-line-height: 1.6 !default;
$base-line-height: 1.4 !default;
```



### (2). 내용의 h1~6, 행간 조정

```_layout.scss
/*
    h2, h3, h4, h5, h6 {
      margin: 60px 0 19px;
    }

    p, hr {
      margin-bottom: 24px;
    }

*/

	h2 {
      margin-top: 30px;
	}

    h3, h4, h5, h6 {
      margin: 10px 0 10px;
    }

    p, hr {
      margin-bottom: 3px;
    }
```


### (3). 포스트 제목 header 조정
```_layout.scss
/**
 * Post header
 */
%post-header {
  .post-header {
    margin-bottom: $spacing-unit;
  }

  .post-title {
    @include relative-font-size(2.625);
    letter-spacing: -1px;
//    line-height: 1.1;
    line-height: 1.0;
```


### (4). 인용부호(<) 폰트 크기 조정
* yat.scss 파일에 $base-font-size 값이 14px 로 지정되어 있으면, 1.125*14px = 15.75px 로 지정된다.

```_base.scss
/**
 * Blockquotes
 */
blockquote {
  color: $grey-color;
  border-left: 4px solid $grey-color-light;
  padding-left: $spacing-unit / 2;
//  @include relative-font-size(1.125);
  @include relative-font-size(1.0);
  letter-spacing: -1px;
  font-style: italic;

  > :last-child {
    margin-bottom: 0;
  }
}
```