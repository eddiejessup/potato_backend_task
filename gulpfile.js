var gulp = require('gulp');
var sass = require('gulp-sass');
var concat = require('gulp-concat');

var baseSrcDir = 'tracker/static-dev';
var baseDestDir = 'tracker/static';

var scssSrcPath = baseSrcDir + '/scss';
var cssSrcPath = baseSrcDir + '/css';
var fontSrcPath = baseSrcDir + '/components/foundation-icon-fonts/foundation-icons.{ttf,woff,eof,svg}';
var jsConcatSrcPaths = [
	baseSrcDir + '/components/fastclick/lib/fastclick.js',
	baseSrcDir + '/components/jquery/dist/jquery.min.js',
	baseSrcDir + '/components/foundation/js/foundation/foundation.min.js',
	baseSrcDir + '/js/app.js'
];
var jsCopySrcPaths = [
    baseSrcDir + '/select2/js/select2.js',
    baseSrcDir + '/select2/js/select2.jquery_ready.js',
	baseSrcDir + '/components/modernizr/modernizr.js'
];

var cssDestPath = baseDestDir + '/css';
var jsDestPath = baseDestDir + '/js';

gulp.task('sass', function () {
    gulp.src(scssSrcPath + '/*.scss')
        .pipe(sass())
        .pipe(gulp.dest(cssSrcPath));
});

gulp.task('copy-foundation-fonts', function () {
	gulp.src(fontSrcPath)
		.pipe(gulp.dest(cssSrcPath));
});

gulp.task('build-styles', ['sass', 'copy-foundation-fonts']);

gulp.task('concat-js', function() {
	gulp.src(jsConcatSrcPaths)
		.pipe(concat('app.built.js'))
		.pipe(gulp.dest(jsDestPath));
});


gulp.task('copy-styles', function () {
	gulp.src(cssSrcPath + '/*.css').pipe(gulp.dest(cssDestPath));
});

gulp.task('copy-js', function () {
	gulp.src(jsCopySrcPaths).pipe(gulp.dest(jsDestPath));
});

gulp.task('build', ['build-styles', 'copy-styles', 'copy-js', 'concat-js'])
gulp.task('default', ['build-styles']);
