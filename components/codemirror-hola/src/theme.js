import {EditorView} from '@codemirror/view';
import {
	HighlightStyle,
	syntaxHighlighting,
} from '@codemirror/language';
import {tags as t} from '@lezer/highlight';


export const createTheme = ({variant, settings, styles}) => {
	const theme = EditorView.theme(
		{
			// eslint-disable-next-line @typescript-eslint/naming-convention
			'&': {
				backgroundColor: settings.background,
				color: settings.foreground,
			},
			'.cm-content': {
				caretColor: settings.caret,
			},
			'.cm-cursor, .cm-dropCursor': {
				borderLeftColor: settings.caret,
			},
			'&.cm-focused .cm-selectionBackground, ::selection':{
				backgroundColor: settings.selection,
			},
			'.cm-activeLine': {
				backgroundColor: settings.lineHighlight,
			},
			'.cm-gutters': {
				backgroundColor: settings.gutterBackground,
				color: settings.gutterForeground,
			},
			'.cm-activeLineGutter': {
				backgroundColor: settings.lineHighlight,
			},
		},
		{
			dark: variant === 'dark',
		},
	);

	const highlightStyle = HighlightStyle.define(styles);
	const extension = [theme, syntaxHighlighting(highlightStyle)];

	return extension;
};


// Author: Chris Kempson
export const tomorrow = createTheme({
	variant: 'light',
	settings: {
		background: '#FFFFFF',
		foreground: '#4D4D4C',
		caret: '#AEAFAD',
		selection: '#A6A6A6',
		gutterBackground: '#FFFFFF',
		gutterForeground: '#4D4D4C80',
		lineHighlight: '#EFEFEF',
	},
	styles: [
		{
			tag: t.comment,
			color: '#8E908C',
		},
		{
			tag: [t.variableName, t.self, t.propertyName, t.attributeName, t.regexp],
			color: '#C82829',
		},
		{
			tag: [t.number, t.bool, t.null],
			color: '#F5871F',
		},
		{
			tag: [t.className, t.typeName, t.definition(t.typeName)],
			color: '#C99E00',
		},
		{
			tag: [t.string, t.special(t.brace)],
			color: '#718C00',
		},
		{
			tag: t.operator,
			color: '#3E999F',
		},
		{
			tag: [t.definition(t.propertyName), t.function(t.variableName)],
			color: '#4271AE',
		},
		{
			tag: t.keyword,
			color: '#8959A8',
		},
		{
			tag: t.derefOperator,
			color: '#4D4D4C',
		},
	],
});